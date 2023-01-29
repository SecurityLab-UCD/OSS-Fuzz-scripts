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
