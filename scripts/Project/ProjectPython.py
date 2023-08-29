import os
import shutil
from os import path
from logging import error, info, warning
from typing import Optional
from scripts.common import OSSFUZZ, OSSFUZZ_SCRIPTS_HOME
from .ProjectBase import Project
from scripts.source_code import py_get_imported_modules
from fuzzywuzzy.fuzz import partial_ratio


class ProjectPython(Project):
    def __init__(self, project: str, fuzzdir: str, dumpdir: str, config: dict):
        super().__init__(project, fuzzdir, dumpdir, config)
        self.fuzzers = [
            f for f in os.listdir(self.project_oss_dir) if f.endswith(".py")
        ]

    def build_w_pass(self, build_script: str = "build_w_pass.sh"):
        dockerfile = f"{OSSFUZZ}/projects/{self.project}/Dockerfile"
        os.system(f"cp {dockerfile} {dockerfile}.bak")
        decorate_fuzzers_config = ["RUN pip3 install python-io-capture"] + [
            f"COPY decorated_{fuzzer} $SRC/{fuzzer}" for fuzzer in self.fuzzers
        ]

        with open(dockerfile, "a") as f:
            f.write("\n".join(decorate_fuzzers_config))

        # backup previous built fuzzers
        build_dir = f"{OSSFUZZ}/build/out/{self.project}"
        if path.isdir(build_dir):
            os.system(f"mv {build_dir} {build_dir}_bak")

        self.build()

        os.system(f"mv {dockerfile}.bak {dockerfile}")

    def auto_build_w_pass(self, cpp: str):
        def transform(code: str, module: str) -> str:
            to_be_inserted = (
                "from py_io_capture import decorate_module, dump_records, DUMP_FILE_NAME"
                "import atexit"
                f"{module} = decorate_module({module})"
                "atexit.register(dump_records, DUMP_FILE_NAME)"
            )
            lines = code.split("\n")
            for i, line in enumerate(lines):
                if "TestOneInput" in line:
                    lines.insert(i + 1, to_be_inserted)
                    break
            return "\n".join(lines)

        for fuzzer in self.fuzzers:
            fuzzer_path = f"{self.project_oss_dir}/{fuzzer}"
            if not path.isfile(fuzzer_path):
                warning(f"{fuzzer_path} not found")
                continue
            with open(fuzzer_path, "r") as f:
                code = f.read()
            target_module = self.get_target_module(code)
            if target_module is None:
                warning(f"Couldn't find target module for {fuzzer_path}")
                continue

            with open(f"decorated_{fuzzer}", "w") as f:
                f.write(transform(code, target_module))

        self.build_w_pass()

    def get_target_module(self, code: str) -> Optional[str]:
        """Get the **most likely** fuzz target module name based on text similarity

        Args:
            code (str): source code of file

        Returns:
            str: the **most likely** target module name
        """
        modules = py_get_imported_modules(code)

        def get_similarity_ration(module):
            return partial_ratio(module, self.project)

        modules.sort(key=get_similarity_ration, reverse=True)
        return modules[0] if len(modules) > 0 else None
