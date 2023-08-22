import os
import shutil
from os import path
from logging import error, info, warning
from scripts.common import OSSFUZZ, OSSFUZZ_SCRIPTS_HOME
from .ProjectBase import Project
from scripts.demangle import main as main_post_process


class ProjectPython(Project):
    def build_w_pass(self, build_script: str = "build_w_pass.sh"):
        raise NotImplementedError

    def auto_build_w_pass(self, cpp: str):
        raise NotImplementedError
