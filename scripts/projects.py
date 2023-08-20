from common import *
from os import path
import os
from logging import error, info, warning

import argparse
import pandas as pd
import yaml
from scripts.util import (
    convert_to_seconds,
)
from scripts.ProjectBase import Project
from scripts.ProjectCpp import ProjectCpp


def main():
    """main script for building a oss-fuzz dataset"""
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

    available_projects = os.listdir(path.join(OSSFUZZ, "projects"))
    if args.dataset not in available_projects:
        unreachable("Unknown dataset provided.")

    project_oss_dir = path.join(OSSFUZZ, "projects", args.dataset)
    with open(f"{project_oss_dir}/project.yaml", "r") as f:
        config = yaml.safe_load(f)
    if config["language"] in ("c", "cpp", "c++"):
        dataset = ProjectCpp(args.dataset, args.fuzzout, args.dumpout, config)
    else:
        dataset = Project(args.dataset, args.fuzzout, args.dumpout, config)

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
    elif args.pipeline == "summarize":
        dataset.summarize()
    else:
        unreachable("Unknown pipeline provided")


# main function
if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    main()
