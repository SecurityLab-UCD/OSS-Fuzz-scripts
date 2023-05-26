from common import *
from os import path
import os
from typing import List, Tuple
from logging import error, info, warning
from functools import partial, reduce
from demangle import extract_func_code, demangle_func, get_source_from_docker
import argparse
import warnings
import shutil
import yaml
from util import (
    oss_fuzz_one_target,
    convert_to_seconds,
)


class Project:
    def __init__(self, project: str, fuzzdir: str, dumpdir: str):
        self.project = project
        self.fuzzdir = path.join(OSSFUZZ_SCRIPTS_HOME, fuzzdir)
        self.dumpdir = path.join(OSSFUZZ_SCRIPTS_HOME, dumpdir)
        self.proj_fuzzout = path.join(self.fuzzdir, self.project)
        self.proj_dumpout = path.join(self.dumpdir, self.project)
        self.targets: List[str] = []
        self.project_oss_dir = path.join(OSSFUZZ, "projects", self.project)
        self.file_func_delim = "?"
        with open(f"{self.project_oss_dir}/project.yaml", "r") as f:
            self.config = yaml.safe_load(f)

    def build(self):
        os.system(
            f"python3 {OSSFUZZ}/infra/helper.py build_fuzzers {self.project} --sanitizer none --clean"
        )
        self._update_targets()

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

    def mkdir_if_doesnt_exist(self):
        if not path.isdir(self.fuzzdir):
            os.makedirs(self.fuzzdir)

        if not path.isdir(self.proj_fuzzout):
            os.makedirs(self.proj_fuzzout)

        if not path.isdir(self.dumpdir):
            os.makedirs(self.dumpdir)

        if not path.isdir(self.proj_dumpout):
            os.makedirs(self.proj_dumpout)

        proj_crash = path.join(self.proj_fuzzout, "crashes")
        if not path.isdir(proj_crash):
            os.makedirs(proj_crash)

        for t in self.targets:
            fuzz_subdir = path.join(self.proj_fuzzout, str(t))
            if not path.isdir(fuzz_subdir):
                os.makedirs(fuzz_subdir)

    def _update_targets(self):
        bindir = path.join(OSSFUZZ, "build/out", self.project)
        if not path.isdir(bindir):
            warning("project build dir doesn't exist, please build the project first")

        # since each projects has its own style of naming fuzzers
        #   w/o fuzzer as substring of fuzzer names
        # and some language projects's fuzzers are not exec
        #   for example, jvm projects have -rwxr--r-- Log4jFuzzer
        # we will just take any file thats not a directory
        # if any of collected files is not actually a fuzzer, the result corpus dir will be just empty
        self.targets = [
            f for f in os.listdir(bindir) if not path.isdir(path.join(bindir, f))
        ]

    def fuzz(self, jobs=CORES, fuzztime=3600, dump=False):
        if not self.targets:
            self._update_targets()

        if not self.targets:
            warning("no targets found, please build fuzzers first")

        self.mkdir_if_doesnt_exist()

        info("Collecting binaries to fuzz")
        bins_to_fuzz: List[Tuple[str, str, str]] = []
        for t in self.targets:
            if "." in t:
                continue
            fuzzout = path.join(self.fuzzdir, self.project, t)
            dumpout = (
                path.join(self.dumpdir, self.project, f"{t}.json") if dump else None
            )
            bins_to_fuzz.append((t, fuzzout, dumpout))

        info(f"Fuzzing all {len(bins_to_fuzz)} binaries for {fuzztime} seconds")
        parallel_subprocess(
            bins_to_fuzz,
            jobs,
            lambda r: oss_fuzz_one_target(r, proj=self.project, fuzztime=fuzztime),
            on_exit=None,
        )

        # redirect all crashes
        crash_dir = path.join(self.fuzzdir, self.project, "crashes")
        outfiles = os.listdir(f"{OSSFUZZ}/build/out/{self.project}")
        if any([f.startswith("crash-") for f in outfiles]):
            os.system(f"mv {OSSFUZZ}/build/out/{self.project}/crash-* {crash_dir}")

    def postprocess(self):
        proj_name = self.project
        json_path = os.path.join(OSSFUZZ_SCRIPTS_HOME, "dump", proj_name)
        json_file_names = [f for f in os.listdir(json_path) if f.endswith(".json")]
        info(f"Looking for json file: {json_file_names}")

        for json_file_name in json_file_names:
            file_name = json_file_name.split(".json")[0]
            # open Json file and get filename+func_name
            with open(os.path.join(json_path, json_file_name), "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    warning(f" {json_file_name}  Json file illegal")
                    continue
            info(f"NUMBER OF FUNCTION: {len(data)}")
            pre_file_path, code_content = "", ""
            for cnt in range(len(data)):
                file_func_name = ""
                for file_func_name_ in data[cnt]:
                    file_func_name = file_func_name_

                # if split not matched, need to add a check
                splited_file_func_name = file_func_name.split(self.file_func_delim)
                file_path, mangle_func_name = (
                    splited_file_func_name[0],
                    splited_file_func_name[1],
                )
                # if this is c file then the mangle does not exist
                try:
                    demangle_func_name = cpp_demangle.demangle(mangle_func_name)
                except ValueError:
                    demangle_func_name = mangle_func_name

                if demangle_func_name == "":  # mangle_func_name == demangle_func_name
                    warning(
                        f" {mangle_func_name} demangle incorrect or unable to demangle"
                    )
                    data[cnt][
                        file_func_name
                    ] = f" {mangle_func_name}demangle incorrect or unable to demangle"
                else:
                    func_name = demangle_func_name.split("(")[0]
                    # Try to get code_content, the json file may provide the path or not
                    # only get code when pre_file_path!=file_path
                    if pre_file_path != file_path:
                        code_content = get_source_from_docker(
                            file_path, file_name, proj_name
                        )
                        pre_file_path = file_path
                        info(f"Open source file: {pre_file_path}")
                        output_path = os.path.join(
                            OSSFUZZ_SCRIPTS_HOME, "output", proj_name
                        )
                        if not os.path.exists(output_path):
                            os.mkdir(output_path)
                        with open(f"{output_path}/{json_file_name}.txt", "w") as fi:
                            # write to JSON file
                            fi.write(code_content)
                    if code_content == "ERROR" or code_content == "":
                        error(f"{json_file_name} CODE content ERROR")
                        pre_file_path = f"try again {cnt}"
                        continue
                    func_content = extract_func_code(func_name, code_content, True)
                    # write to json
                    data[cnt][file_func_name] = {
                        "code": func_content,
                        "data": data[cnt][file_func_name],
                    }
            # open the file for writing
            with open(
                os.path.join(OSSFUZZ_SCRIPTS_HOME, "output", proj_name, json_file_name),
                "w",
            ) as json_file:
                # write to JSON file
                json.dump(data, json_file)

    def summarize(self):
        pass

    def auto_build_w_pass(self, cpp: str):
        """build a project with pass automaticly

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

    def _is_auto_supported(self):
        lang = self.config["language"]
        supported_langs = ["c", "cpp", "c++"]
        return lang.lower() in supported_langs


def main():
    parser = argparse.ArgumentParser(description="Build a dataset")
    parser.add_argument(
        "-d",
        "--dataset",
        type=str,
        required=True,
        help="The dataset to build",
    )
    parser.add_argument(
        "-o",
        "--fuzzout",
        type=str,
        help="directory to store corpus for the fuzz target",
        default="fuzz",
    )
    parser.add_argument(
        "--dumpout",
        type=str,
        help="directory to store JSON files for the IO dump",
        default="dump",
    )
    parser.add_argument(
        "-j", "--jobs", type=int, help="Number of threads to use.", default=CORES
    )
    parser.add_argument(
        "-p",
        "--pipeline",
        type=str,
        help="The stage of the job to run",
        default="all",
        choices=[
            "all",
            "build",
            "build_w_pass",
            "auto_build_w_pass",
            "fuzz",
            "fuzz_w_pass",
            "postprocess",
            "summarize",
        ],
    )
    parser.add_argument(
        "-ft", "--fuzztime", type=str, help="Time to fuzz one program", default="1m"
    )
    parser.add_argument(
        "--cpp",
        type=str,
        help="stdc++ or c++",
        default="stdc++",
        choices=["stdc++", "c++"],
    )

    args = parser.parse_args()

    aviliable_porjects = os.listdir(path.join(OSSFUZZ, "projects"))
    if args.dataset not in aviliable_porjects:
        unreachable("Unknown dataset provided.")

    dataset = Project(args.dataset, args.fuzzout, args.dumpout)

    if args.pipeline == "all":
        dataset.build()
        dataset.fuzz(jobs=args.jobs, fuzztime=convert_to_seconds(args.fuzztime))
    elif args.pipeline == "build":
        dataset.build()
    elif args.pipeline == "build_w_pass":
        dataset.build_w_pass()
    elif args.pipeline == "auto_build_w_pass":
        dataset.auto_build_w_pass(cpp=args.cpp)
    elif args.pipeline == "fuzz":
        dataset.fuzz(jobs=args.jobs, fuzztime=convert_to_seconds(args.fuzztime))
    elif args.pipeline == "fuzz_w_pass":
        info("fuzzing with pass, please make sure you have built the project with pass")
        dataset.fuzz(
            jobs=args.jobs, fuzztime=convert_to_seconds(args.fuzztime), dump=True
        )
    elif args.pipeline == "postprocess":
        dataset.postprocess()
    else:
        unreachable("Unkown pipeline provided")


# main function
if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    main()
