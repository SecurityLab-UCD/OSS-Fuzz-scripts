import sys
import os
import pandas as pd

from scripts.common import *
from scripts.projects import Project
from scripts.fuzzer_stats import FuzzerStats, summarize_fuzzer_stats_df


def get_project_fuzzer_stats(project: str) -> pd.DataFrame:
    fuzzout = "fuzz"
    dumpout = "dump"
    proj = Project(project, fuzzout, dumpout)
    return proj.get_project_stats()


def main():
    projects = ["coturn", "json-c"]  # todo: full list of built & fuzzed projects

    df = pd.concat([get_project_fuzzer_stats(project) for project in projects])
    print(f"In all {len(projects)} built and fuzzed projects:")
    summarize_fuzzer_stats_df(df)
    return 0


if __name__ == "__main__":
    sys.exit(main())
