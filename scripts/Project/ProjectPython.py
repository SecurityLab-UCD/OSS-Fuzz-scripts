import os
import shutil
from os import path
from logging import error, info, warning
from scripts.common import OSSFUZZ, OSSFUZZ_SCRIPTS_HOME
from .ProjectBase import Project
from scripts.demangle import main as main_post_process


class ProjectPython(Project):
    def build_w_pass(self, build_script: str = "build_w_pass.sh"):
        dockerfile = f"{OSSFUZZ}/projects/{self.project}/Dockerfile"
        os.system(f"cp {dockerfile} {dockerfile}.bak")
        install_py_io_capture = "pip3 install python-io-capture"

        with open(dockerfile, "a") as f:
            f.write(install_py_io_capture)

        # backup previous built fuzzers
        build_dir = f"{OSSFUZZ}/build/out/{self.project}"
        if path.isdir(build_dir):
            os.system(f"mv {build_dir} {build_dir}_bak")

        self.build()

        os.system(f"mv {dockerfile}.bak {dockerfile}")

    def auto_build_w_pass(self, cpp: str):
        raise NotImplementedError
