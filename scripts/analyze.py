import sys
import os
import pandas as pd
import re

from scripts.common import *
from scripts.projects import Project
from scripts.fuzzer_stats import FuzzerStats, summarize_fuzzer_stats_df


def get_project_fuzzer_stats(project: str) -> pd.DataFrame:
    fuzzout = "fuzz"
    dumpout = "dump"
    proj = Project(project, fuzzout, dumpout)
    return proj.get_project_stats()

def get_proj_name(line: str) -> Optional[str]:
    #pattern = '^[0-9]+\. \[?([A-Za-z0-9\-\_]+)\]?\([A-Za-z\.\_\-/ +]+\),([A-Za-z+]+)'
    # Group 1 is project name, group 2 is project language
    pattern = '^[0-9]+\. \[?([^\]]+)\]?\(.+\),([A-Za-z+]+)'
    
    line = line.strip()  # remove space at front and end
    match = re.match(pattern, line)

    if not match:
        return None
    
    proj_name = match.group(1)
    proj_language = match.group(2)
    return proj_name

def main():
    
    with open("./built_w_pass.md", "r") as f:
        lines = f.readlines()
    projects = list(filter(lambda x: x is not None, map(get_proj_name, lines))) 
    #projects = ["clib", "coturn", "croaring", "gpac", "h3", "inchi", "libdwarf", "libpg_query", "libssh", "libyang", "lua",
    #        "llhttp", "md4c", "miniz", "tmux", "p11-kit", "pycryptodome", "quickjs", "utf8proc", "w3m", "zydis"]  # todo: full list of built & fuzzed projects

    df = pd.concat([get_project_fuzzer_stats(project) for project in projects])
    print(f"In all {len(projects)} built and fuzzed projects:")
    summarize_fuzzer_stats_df(df)
    return 0


if __name__ == "__main__":
    sys.exit(main())
