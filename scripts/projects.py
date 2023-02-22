from common import *
from os import path
import os
from typing import List, Tuple
from logging import error, info, warning
from functools import partial, reduce
import argparse
import warnings
from util import oss_fuzz_one_target, convert_to_seconds


# def fuzz_all(project_names: List[str], fuzzout: str, jobs: int, fuzztime: int):
#     projects = [Project(n, fuzzout) for n in project_names]
#     all_bins = reduce(
#         lambda xs, ys: xs + ys, map(lambda p: p.collect_bins_to_fuzz(), projects)
#     )
#     parallel_subprocess(
#         all_bins,
#         jobs,
#         lambda r: oss_fuzz_one_target(r, proj=project, fuzztime=fuzztime),
#         on_exit=None,
#     )
#     pass


class Project:
    def __init__(self, project: str, fuzzdir: str):
        self.project = project
        self.fuzzdir = path.join(DETECTION_HOME, fuzzdir)
        self.targets: List[str] = []

    def build(self):
        os.system(f"python3 {OSSFUZZ}/infra/helper.py build_fuzzers {self.project}")
        self._update_targets()

    def mkdir_if_doesnt_exist(self):
        if not path.isdir(self.fuzzdir):
            os.makedirs(self.fuzzdir)

        proj_fuzzout = path.join(self.fuzzdir, self.project)
        if not path.isdir(proj_fuzzout):
            os.makedirs(proj_fuzzout)

        proj_crash = path.join(proj_fuzzout, "crashes")
        if not path.isdir(proj_crash):
            os.makedirs(proj_crash)

        for t in self.targets:
            subdir = path.join(proj_fuzzout, str(t))
            if not path.isdir(subdir):
                os.makedirs(subdir)

    def _update_targets(self):
        bindir = path.join(OSSFUZZ, "build/out", self.project)
        if not path.isdir(bindir):
            warning("project build dir doesn't exist, please build the project first")
        for f in os.listdir(bindir):
            fpath = path.join(bindir, f)
            if os.access(fpath, os.X_OK) and not path.isdir(fpath):
                self.targets.append(f)

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
            "fuzz",
            "postprocess",
            "summarize",
        ],
    )
    parser.add_argument(
        "-ft", "--fuzztime", type=str, help="Time to fuzz one program", default="1h"
    )

    args = parser.parse_args()

    aviliable_porjects = os.listdir(path.join(OSSFUZZ, "projects"))
    if args.dataset not in aviliable_porjects:
        unreachable("Unknown dataset provided.")

    dataset = Project(args.dataset, args.fuzzout)

    if args.pipeline == "all":
        dataset.build()
        dataset.fuzz(jobs=args.jobs, fuzztime=convert_to_seconds(args.fuzztime))
    elif args.pipeline == "build":
        dataset.build()
    elif args.pipeline == "fuzz":
        dataset.fuzz(jobs=args.jobs, fuzztime=convert_to_seconds(args.fuzztime))
    else:
        unreachable("Unkown pipeline provided")


# main function
if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    main()
