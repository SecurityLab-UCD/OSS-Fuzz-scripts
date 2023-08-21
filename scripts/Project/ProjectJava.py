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
        """build a project with pass automatically

        Args:
            cpp (str): stdc++ or c++
        """
        build_sh = path.join(self.project_oss_dir, "build.sh")
        build_w_pass_sh = path.join(self.project_oss_dir, "build_w_pass.sh")
        if path.isfile(build_w_pass_sh):
            info("build_w_pass.sh already exists")
            self.build_w_pass()
            return

        if not self._is_auto_supported():
            warning(f"auto build is not supported for {self.config['language']}")
            return

        with open(build_sh, "r") as f:
            build_lines = f.readlines()

        jvm_arg_w_agent = '--jvm_args="-javaagent:$REPORT_AGENT" \\'
        for i, line in reversed(list(enumerate(build_lines))):
            if line.startswith("—jvm_args="):
                build_lines[i] = jvm_arg_w_agent
                break  # Exit the loop if the first occurrence is replaced

        with open(build_w_pass_sh, "w") as f:
            f.writelines(build_lines)

        self.build_w_pass()
        os.remove(build_w_pass_sh)

    def postprocess(self):
        raise NotImplementedError
