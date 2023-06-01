import logging
from logging import error, info, warning
import os
from os import path
from typing import Iterable, Callable, Set, Tuple, TypeVar, Optional, Dict
import subprocess
from tqdm import tqdm
import socket


OSSFUZZ = os.getenv("OSSFUZZ")
if OSSFUZZ == None:
    error("OSSFUZZ not set, please tell me where oss-fuzz is.")
    exit(1)

FILE_FUNC_DELIM = "?"

LLVM = os.getenv("LLVM")
if LLVM == None:
    error("LLVM not set, please tell me where clang+llvm is.")
    exit(1)

CORES = os.getenv("CORES")
if CORES == None:
    import multiprocessing

    CORES = multiprocessing.cpu_count()
    warning(f"CORES not set, default to all cores. (nproc = {CORES})")

OSSFUZZ_SCRIPTS_HOME = os.getenv("OSSFUZZ_SCRIPTS_HOME")
if OSSFUZZ_SCRIPTS_HOME == None:
    error("OSSFUZZ_SCRIPTS_HOME not set, please tell me where the code is.")
    exit(1)

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
    The return valus is a dictionary of inputs and outputs.

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


class ExprimentInfo:
    expr_path: str
    fuzzed: bool

    def __init__(self, expr_path):
        self.expr_path = expr_path
        self.fuzzed = True
        try:
            with open(self.get_fuzzer_stats_path(), "r") as f:
                for line in f:
                    line = line.split(" : ")
                    self.__dict__[line[0].strip()] = line[1]
            self.run_time = int(self.run_time)
            self.bitmap_cvg = float(self.bitmap_cvg[:-2])
            self.execs_per_sec = float(self.execs_per_sec)
            self.execs_done = int(self.execs_done)
        except:
            self.fuzzed = False

    def sufficiently_fuzzed(self):
        return self.fuzzed and (self.bitmap_cvg > 50.0 or self.run_time > 30)

    def to_expr_path(self):
        return self.expr_path

    def get_fuzzer_stats_path(self):
        return os.path.join(self.to_expr_path(), "default", "fuzzer_stats")

    def get_plot_data_path(self):
        return os.path.join(self.to_expr_path(), "default", "plot_data")
