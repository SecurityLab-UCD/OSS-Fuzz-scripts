import os
import shutil
from os import path
from logging import error, info, warning
from scripts.common import OSSFUZZ, OSSFUZZ_SCRIPTS_HOME
from scripts.ProjectBase import Project
from scripts.demangle import main as main_post_process


class ProjectCpp(Project):
    def build_w_pass(self, build_script: str = "build_w_pass.sh"):
        dockerfile = f"{OSSFUZZ}/projects/{self.project}/Dockerfile"
        os.system(f"cp {dockerfile} {dockerfile}.bak")
        os.system(
            f"rsync -av --exclude='.*' {OSSFUZZ_SCRIPTS_HOME}/ReportFunctionExecutedPass {OSSFUZZ}/projects/{self.project}"
        )
        report_pass_config = (
            f"ENV REPORT_PASS=$SRC/{self.project}/ReportFunctionExecutedPass\n"
            f"COPY {build_script} $SRC/build.sh\n"
            "COPY ReportFunctionExecutedPass $REPORT_PASS\n"
            "RUN cd $REPORT_PASS && ./init.sh\n"
        )

        with open(dockerfile, "a") as f:
            f.write("".join(report_pass_config))

        # backup previous built fuzzers
        build_dir = f"{OSSFUZZ}/build/out/{self.project}"
        if path.isdir(build_dir):
            os.system(f"mv {build_dir} {build_dir}_bak")

        self.build()

        os.system(f"mv {dockerfile}.bak {dockerfile}")
        shutil.rmtree(f"{OSSFUZZ}/projects/{self.project}/ReportFunctionExecutedPass")

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

        common_report_flags = [
            'REPORT_FLAGS="-Xclang -load -Xclang $REPORT_PASS/libReportPass.so -flegacy-pass-manager"\n',
            f'REPORTER_FLAGS="$REPORT_PASS/reporter.{cpp}.o -l{cpp} -pthread -lm"\n',
            'export CFLAGS="${CFLAGS:=} $REPORT_FLAGS $REPORTER_FLAGS"\n',
            'export CXXFLAGS="${CXXFLAGS:=} $REPORT_FLAGS $REPORTER_FLAGS"\n',
        ]

        with open(build_sh, "r") as f:
            build_lines = f.readlines()

        # todo: find better way to insert the flags
        # for now, just hope this comment is build.sh
        build_comment = f"# build {self.project}\n"
        insertion_point = (
            build_lines.index(build_comment) if build_comment in build_lines else 1
        )
        build_w_pass_lines = (
            build_lines[:insertion_point]
            + common_report_flags
            + build_lines[insertion_point:]
        )
        with open(build_w_pass_sh, "w") as f:
            f.writelines(build_w_pass_lines)

        self.build_w_pass()
        os.remove(build_w_pass_sh)

    def postprocess(self):
        proj_name = self.project
        main_post_process(proj_name, self.config["language"])
