import subprocess
import random
import re
from logging import error
from common import *
from typing import Tuple


def oss_fuzz_one_target(
    p: Tuple[str, str, str | None], proj: str, fuzztime: int
) -> subprocess.Popen:
    target, fuzzout, dump = p
    cmd = [
        "python3",
        f"{OSSFUZZ}/infra/helper.py",
        "run_fuzzer",
        proj,
        target,
        f"\-max_total_time={fuzztime}",
        "\-rss_limit_mb=0",
        "--engine",
        "libfuzzer",
        "--corpus-dir",
        fuzzout,
    ]

    if dump is not None:
        cmd += [
            "-e",
            f"DUMP_FILE_NAME={dump}",
        ]

    job = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return job


def run_one_fuzzer(p, runtime):
    """Deprecated, the function is left as a placeholder for future to
    find a way for libFuzzer to run without refuzzing
    """
    warning("run_one_fuzzer is deprecated, please use oss_fuzz_one_target instead")
    target, corpus_dir, dump = p
    cmd = [
        target,
        "-rss_limit_mb=0",
        f"-max_total_time={runtime}",
        # todo: find a way for libFuzzer to run without refuzzing
        # "--corpus-dir",
        # corpus_dir,
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
