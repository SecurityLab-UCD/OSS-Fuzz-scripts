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
            f
            for f in os.listdir(self.project_oss_dir)
            if f.endswith(".py") and f.startswith("fuzz_")
        ]

    def build(self):
        os.system(
            f"python3 {OSSFUZZ}/infra/helper.py build_fuzzers {self.project} --sanitizer coverage --clean"
        )
        self._update_targets()

    def build_w_pass(self, build_script: str = "build_w_pass.sh"):
        dockerfile = f"{OSSFUZZ}/projects/{self.project}/Dockerfile"
        decorate_fuzzers_config = [
            "RUN pip3 install git+https://github.com/SecurityLab-UCD/python-io-capture.git --force-reinstall",
            "RUN pip3 install StrEnum",
        ] + [f"COPY decorated_{fuzzer} $SRC/{fuzzer}" for fuzzer in self.fuzzers]

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
        def transform(code: str) -> str:
            # List of tuples of module name and whether to import the module
            modules = []
            ignore = {"atheris", "sys"}
            from_import = "from .* import .*"
            lines = code.split("\n")
            for i, line in enumerate(lines):
                # If function definition, assume import statements are done
                if "def " in line:
                    # Add decorated modules one by one from module list
                    to_be_inserted = (
                        "from py_io_capture import decorate_module, dump_records, DUMP_FILE_NAME\n"
                        "import atexit\n"
                        "atexit.register(dump_records, DUMP_FILE_NAME)\n"
                    )
                    for module, imprt in modules:
                        if imprt:
                            to_be_inserted += f"import {module}\n"
                        to_be_inserted += f"{module} = decorate_module({module})\n"
                    lines.insert(i - 1, to_be_inserted)
                    break
                elif re.match(from_import, line):
                    module = line.split(" ")[1]
                    if module in ignore:
                        continue
                    modules.append((module, True))
                elif "import " in line:
                    # Some import statements have multiple modules imported
                    imported_modules = line.split("import ")[1].split(", ")
                    for module in imported_modules:
                        if module in ignore:
                            continue
                        modules.append((module, False))
            return "\n".join(lines)

        for fuzzer in self.fuzzers:
            fuzzer_path = f"{self.project_oss_dir}/{fuzzer}"
            if not path.isfile(fuzzer_path):
                warning(f"{fuzzer_path} not found")
                continue
            with open(fuzzer_path, "r") as f:
                code = f.read()
            with open(f"{self.project_oss_dir}/decorated_{fuzzer}", "w") as f:
                f.write(transform(code))

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
