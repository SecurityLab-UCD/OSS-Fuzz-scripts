import subprocess
import random
import re
from logging import error
from common import *


def oss_fuzz_one_target(p, proj, fuzztime):
    target, fuzzout = p
    return subprocess.Popen(
        [
            "python3",
            f"{OSSFUZZ}/infra/helper.py",
            "run_fuzzer",
            proj,
            target,
            f"\-max_total_time={fuzztime}",
            "--engine",
            "libfuzzer",
            "--corpus-dir",
            fuzzout,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def run_one_fuzzer(p, runtime):
    target, corpus_dir, dump = p
    cmd = [
        target,
        "-rss_limit_mb=0",
        f"-max_total_time={runtime}",
        "--corpus-dir",
        corpus_dir,
    ]
    with open(dump, "w") as dumpfile:
        return subprocess.Popen(
            cmd,
            stdout=dumpfile,
            stderr=subprocess.DEVNULL,
        )


def convert_to_seconds(s: str) -> int:
    seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    return int(s[:-1]) * seconds_per_unit[s[-1]]
