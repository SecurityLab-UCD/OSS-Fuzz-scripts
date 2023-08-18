import logging
from logging import error, info, warning
import os
from os import path
from typing import Iterable, Callable, Set, Tuple, TypeVar, Optional, Dict
import subprocess
from tqdm import tqdm
from enum import IntEnum

OSSFUZZ = os.getenv("OSSFUZZ")
if OSSFUZZ is None:
    error("OSSFUZZ not set, please tell me where oss-fuzz is.")
    exit(1)
else:
    OSSFUZZ = os.path.abspath(OSSFUZZ)

FILE_FUNC_DELIM = "?"

LLVM = os.getenv("LLVM")
if LLVM == None:
    error("LLVM not set, please tell me where clang+llvm is.")
    exit(1)

LIBCLANG = os.path.join(LLVM, "lib", "libclang.so")
if not path.exists(LIBCLANG):
    error(f"libclang.so not found at {LIBCLANG}, please check LLVM.")
    exit(1)

CORES = os.getenv("CORES")
if CORES == None:
    import multiprocessing

    CORES = multiprocessing.cpu_count()
    warning(f"CORES not set, default to all cores. (nproc = {CORES})")

OSSFUZZ_SCRIPTS_HOME = os.getenv("OSSFUZZ_SCRIPTS_HOME")
if OSSFUZZ_SCRIPTS_HOME is None:
    error("OSSFUZZ_SCRIPTS_HOME not set, please tell me where the code is.")
    exit(1)
else:
    OSSFUZZ_SCRIPTS_HOME = os.path.abspath(OSSFUZZ_SCRIPTS_HOME)

__T = TypeVar("__T")
__R = TypeVar("__R")


def unreachable(s: str = ""):
    error(f"Unreachable executed: {s}")
    exit(1)


def parallel_subprocess(
    iter: Iterable[__T],
    jobs: int,
    subprocess_creator: Callable[[__T], subprocess.Popen],
    on_exit: Optional[Callable[[subprocess.Popen], __R]] = None,
    use_tqdm=True,
    tqdm_leave=True,
    tqdm_msg="",
) -> Dict[__T, __R]:
    """
    Creates `jobs` subprocesses that run in parallel.
    `iter` contains input that is send to each subprocess.
    `subprocess_creator` creates the subprocess and returns a `Popen`.
    After each subprocess ends, `on_exit` will go collect user defined input and return.
    The return values is a dictionary of inputs and outputs.

    User has to guarantee elements in `iter` is unique, or the output may be incorrect.
    """
    ret = {}
    processes: Set[Tuple[subprocess.Popen, __T]] = set()
    if use_tqdm:
        iter = tqdm(iter, leave=tqdm_leave, desc=tqdm_msg)
    for input in iter:
        processes.add((subprocess_creator(input), input))
        if len(processes) >= jobs:
            # wait for a child process to exit
            os.wait()
            exited_processes = [(p, i) for p, i in processes if p.poll() is not None]
            for p, i in exited_processes:
                processes.remove((p, i))
                if on_exit is not None:
                    ret[i] = on_exit(p)
    # wait for remaining processes to exit
    for p, i in processes:
        p.wait()
        # let `on_exit` to decide wait for or kill the process
        if on_exit is not None:
            ret[i] = on_exit(p)
    return ret


class SourceCodeStatus(IntEnum):
    SUCCESS = 1  # Found source code
    TEMPLATE = 2  # Template function (only applicable for C++ source code)
    NOT_FOUND = 3  # Couldn't find source code
    DEMANGLE_ERROR = 4  # Could be TEMPLATE or NOT_FOUND, couldn't demangle to check
    PATH_ERROR = 5  # Source code path specified in JSON file could not be found

