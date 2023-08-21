import os
import shutil
from os import path
from logging import error, info, warning
from scripts.common import OSSFUZZ, OSSFUZZ_SCRIPTS_HOME
from .ProjectBase import Project
from scripts.demangle import main as main_post_process


class ProjectJava(Project):
    def build(self):
        # ! test on antlr4-java
        # --sanitizer none will cause build failure
        # to reproduce, run one of the following commands
        # python3 ./oss-fuzz/infra/helper.py build_fuzzers antlr4-java --sanitizer none
        os.system(f"python3 {OSSFUZZ}/infra/helper.py build_fuzzers {self.project}")
        self._update_targets()

    def build_w_pass(self, build_script: str = "build_w_pass.sh"):
        dockerfile = f"{OSSFUZZ}/projects/{self.project}/Dockerfile"
        os.system(f"cp {dockerfile} {dockerfile}.bak")
        agent = "java-io-capture-1.0-SNAPSHOT.jar"
        shutil.copyfile(
            f"{OSSFUZZ_SCRIPTS_HOME}/java-io-capture/target/{agent}",
            f"{OSSFUZZ}/projects/{self.project}/{agent}",
        )
        # some project's path is not its name
        # for example, the project name is "antlr4-java",
        # but the path is "antlr4"
        report_agent_config = (
            f"ENV REPORT_AGENT=$SRC/{agent}\n"
            f"COPY {build_script} $SRC/build.sh\n"
            f"COPY {agent} $REPORT_AGENT\n"
        )

        with open(dockerfile, "a") as f:
            f.write("".join(report_agent_config))

        # backup previous built fuzzers
        build_dir = f"{OSSFUZZ}/build/out/{self.project}"
        if path.isdir(build_dir):
            os.system(f"mv {build_dir} {build_dir}_bak")

        self.build()

        os.system(f"mv {dockerfile}.bak {dockerfile}")
        os.remove(f"{OSSFUZZ}/projects/{self.project}/{agent}")

    def auto_build_w_pass(self, cpp: str):
        raise NotImplementedError

    def postprocess(self):
        raise NotImplementedError
