from common import *
from os import path
import os
from typing import List, Tuple
from logging import error, info, warning
from functools import partial, reduce
import argparse
import warnings
import shutil
import yaml
from util import (
    oss_fuzz_one_target,
    convert_to_seconds,
    run_one_fuzzer,
)


class Project:
    def __init__(self, project: str, fuzzdir: str, dumpdir: str):
        self.project = project
        self.fuzzdir = path.join(OSSFUZZ_SCRIPTS_HOME, fuzzdir)
        self.dumpdir = path.join(OSSFUZZ_SCRIPTS_HOME, dumpdir)
        self.proj_fuzzout = path.join(self.fuzzdir, self.project)
        self.proj_dumpout = path.join(self.dumpdir, self.project)
        self.targets: List[str] = []
        with open(f"{OSSFUZZ}/projects/{project}/project.yaml", "r") as f:
            self.config = yaml.safe_load(f)

    def build(self):
        os.system(
            f"python3 {OSSFUZZ}/infra/helper.py build_fuzzers {self.project} --sanitizer none"
        )
        self._update_targets()

    def build_w_pass(self):
        dockerfile = f"{OSSFUZZ}/projects/{self.project}/Dockerfile"
        os.system(f"cp {dockerfile} {dockerfile}.bak")
        os.system(
            f"rsync -av --exclude='.*' {OSSFUZZ_SCRIPTS_HOME}/ReportFunctionExecutedPass {OSSFUZZ}/projects/{self.project}"
        )
        report_pass_config = (
            f"ENV REPORT_PASS=$SRC/{self.project}/ReportFunctionExecutedPass\n"
            "COPY build_w_pass.sh $SRC/build.sh\n"
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

    def fuzz(self, jobs=CORES, fuzztime=3600):
        if not self.targets:
            self._update_targets()

        if not self.targets:
            warning("no targets found, please build fuzzers first")

        self.mkdir_if_doesnt_exist()

        info("Collecting binaries to fuzz")
        bins_to_fuzz = [
            (t, path.join(self.fuzzdir, self.project, t)) for t in self.targets
        ]

        info(f"Fuzzing all {len(bins_to_fuzz)} binaries for {fuzztime} seconds")
        parallel_subprocess(
            bins_to_fuzz,
            jobs,
            lambda r: oss_fuzz_one_target(r, proj=self.project, fuzztime=fuzztime),
            on_exit=None,
        )

        # redirect all crashes
        crash_dir = path.join(self.fuzzdir, self.project, "crashes")
        os.system(f"mv {OSSFUZZ}/build/out/{self.project}/crash-* {crash_dir}")

    def fuzz_w_pass(self, runtime=1, jobs=CORES):
        if not self.targets:
            self._update_targets()

        if not self.targets:
            warning("no targets found, please build fuzzers first")

        self.mkdir_if_doesnt_exist()

        info("Collecting binaries to run")
        bins_to_run: List[Tuple[str, str, str]] = []
        for t in self.targets:
            if "." in t:
                continue
            fuzzer = path.join(OSSFUZZ, "build", "out", self.project, t)
            corpus = path.join(self.proj_fuzzout, t)
            dump = path.join(self.proj_dumpout, f"{t}.json")
            bins_to_run.append((fuzzer, corpus, dump))

        info(f"Fuzzing all {len(bins_to_run)} binaries for {runtime} seconds")
        parallel_subprocess(
            bins_to_run,
            jobs,
            lambda r: run_one_fuzzer(r, runtime=runtime),
            on_exit=None,
        )

    def postprocess(self):
        pass

    def summarize(self):
        pass


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
            "fuzz",
            "fuzz_w_pass",
            "postprocess",
            "summarize",
        ],
    )
    parser.add_argument(
        "-ft", "--fuzztime", type=str, help="Time to fuzz one program", default="1h"
    )
    parser.add_argument(
        "-rt", "--runtime", type=str, help="Time to run one program", default="1s"
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
    elif args.pipeline == "fuzz":
        dataset.fuzz(jobs=args.jobs, fuzztime=convert_to_seconds(args.fuzztime))
    elif args.pipeline == "fuzz_w_pass":
        dataset.fuzz_w_pass(jobs=args.jobs, runtime=convert_to_seconds(args.runtime))
    elif args.pipeline == "postprocess":
        dataset.postprocess()
    else:
        unreachable("Unkown pipeline provided")


# main function
if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    main()
