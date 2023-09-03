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

    def build(self):
        os.system(
            f"python3 {OSSFUZZ}/infra/helper.py build_fuzzers {self.project} --sanitizer coverage --clean"
        )
        self._update_targets()

    def build_w_pass(self, build_script: str = "build_w_pass.sh"):
        dockerfile = f"{OSSFUZZ}/projects/{self.project}/Dockerfile"
        decorate_fuzzers_config = ["RUN pip3 install python-io-capture"] + [
            f"COPY decorated_{fuzzer} $SRC/{fuzzer}" for fuzzer in self.fuzzers
        ]

        # Only create new Dockerfile if haven't already
        if not os.path.exists(f"{dockerfile}.bak"):
            os.system(f"cp {dockerfile} {dockerfile}.bak")
            with open(dockerfile, "a") as f:
                f.write("\n".join(decorate_fuzzers_config))
                f.write("\n")

        # backup previous built fuzzers
        build_dir = f"{OSSFUZZ}/build/out/{self.project}"
        if path.isdir(build_dir):
            os.system(f"mv {build_dir} {build_dir}_bak")

        self.build()

        os.system(f"mv {dockerfile}.bak {dockerfile}")

    def auto_build_w_pass(self, cpp: str):
        def transform(code: str, module: str) -> str:
            to_be_inserted = (
                "from py_io_capture import decorate_module, dump_records, DUMP_FILE_NAME\n"
                "import atexit\n"
                f"{module} = decorate_module({module})\n"
                "atexit.register(dump_records, DUMP_FILE_NAME)\n"
            )
            lines = code.split("\n")
            for i, line in enumerate(lines):
                if "TestOneInput" in line:
                    lines.insert(i - 1, to_be_inserted)
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

            with open(f"{self.project_oss_dir}/decorated_{fuzzer}", "w") as f:
                f.write(transform(code, target_module))

        self.build_w_pass()
        
        # Remove decorated_{fuzzer} files
        for fuzzer in self.fuzzers:
            fuzzer_path = f"{self.project_oss_dir}/{fuzzer}"
            if not path.isfile(fuzzer_path):
                warning(f"{fuzzer_path} not found")
                continue
            os.system(f"rm {self.project_oss_dir}/decorated_{fuzzer}")

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
