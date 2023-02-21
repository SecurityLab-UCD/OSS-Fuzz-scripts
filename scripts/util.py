import subprocess
import random
import re
from logging import error
from common import *


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
