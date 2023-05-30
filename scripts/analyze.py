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
    projects = ["clib", "cjson", "coturn", "croaring", "gpac", "h3", "inchi", "libdwarf", "libpg_query", "libssh", "libyang",
            "llhttp", "md4c", "miniz", "tmux", "p11-kit", "pycryptodome", "quickjs", "utf8proc", "w3m", "zydis"]  # todo: full list of built & fuzzed projects

    df = pd.concat([get_project_fuzzer_stats(project) for project in projects])
    print(f"In all {len(projects)} built and fuzzed projects:")
    summarize_fuzzer_stats_df(df)
    return 0


if __name__ == "__main__":
    sys.exit(main())
