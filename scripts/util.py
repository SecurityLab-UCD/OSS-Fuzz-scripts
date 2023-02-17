import subprocess
import random
import re
from logging import error
from common import *


def fuzz_one_instance(
    p: Tuple[str, str, str, bool, str],
    timeout: int,
    seeds: str,
):
    binary, out, instance, node_type = p
    cmd = [
        f"{AFL}/afl-fuzz",
        "-D",
        "-V",
        str(timeout),
        node_type,
        instance,
        "-i",
        seeds,
        "-o",
        out,
        binary,
        "-i",
        "@@",
    ]
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    # Sleep half a second for AFL to bind core.
    subprocess.run(["sleep", "0.5"])
    return process


def oss_fuzz_one_target(p, proj, fuzztime):
    target, fuzzout = p
    "python infra/helper.py run_fuzzer qemu qemu-fuzz-i386-target-generic-fuzz-virtio-gpu  qemu-seeds"
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
