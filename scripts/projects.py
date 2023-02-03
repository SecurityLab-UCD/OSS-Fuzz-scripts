from common import *
from os import path
import os
from typing import List, Tuple
from logging import error, info, warning
from functools import partial
import argparse
import warnings
from util import fuzz_one_instance


class Project:
    seeds_dir: str = ""
    target: str = ""

    def __init__(self):
        pass

    def get_seeds(self):
        pass

    def fuzz(self, jobs=CORES, timeout=3600):
        if not path.isdir("fuzz"):
            os.mkdir("fuzz")
        out = "fuzz"
        to_fuzz = [(self.target, out, "fuzzer0", "-M")]
        to_fuzz += [(self.target, out, f"fuzzer{i}", "-S") for i in range(1, jobs)]
        print(len(to_fuzz))
        print(timeout)
        subprocess.run(["sleep", "0.5"])
        parallel_subprocess(
            to_fuzz,
            jobs,
            lambda r: fuzz_one_instance(r, timeout=timeout, seeds=self.seeds),
            use_tqdm=False,
        )

    def summarize(self):
        pass


class FFmpeg(Project):
    def __init__(self, seeds_dir):
        Project.__init__(self)
        self.seeds = path.join(seeds_dir, "ffmpeg")
        self.target = f"{FFMPEG}/ffmpeg"

    def get_seeds(self, jobs: int = CORES):
        # http://samples.ffmpeg.org/
        domain = "samples.ffmpeg.org"
        seeds = ["A-codecs", "AVS"]
        for s in tqdm(seeds):
            subprocess.run(["wget", "-r", "--no-parent", f"https://{domain}/{s}"])
        os.system(
            f"{AFL}/afl-cmin -i {domain} -o minffmpeg -- {self.target} -i @@ ffmpeg"
        )
        os.system(f"rm {domain}; mv minffmpeg {self.seeds}")


class Qemu(Project):
    def __init__(self, seeds_dir="seeds"):
        Project.__init__(self)
        self.seeds = path.join(seeds_dir, "qemu")
        self.target = f"{QEMU}/build/qemu-x86_64"

    def get_seeds(self):
        if not os.path.isdir(self.seeds):
            info(f"make new directory at {self.seeds}")
            os.mkdir(self.seeds)
        os.system(
            f"{AFL}/afl-cmin -i {QEMU}/tests/ -o minqemu -- {self.target} -i @@ qemu"
        )
        os.system(f"mv minqemu {self.seeds}")


def main():
    parser = argparse.ArgumentParser(description="Build a dataset")
    parser.add_argument(
        "-d",
        "--dataset",
        type=str,
        choices=["FFmpeg", "qemu"],
        required=True,
        help="The dataset to compile",
    )
    parser.add_argument(
        "-j", "--jobs", type=int, help="Number of threads to use.", default=CORES
    )
    parser.add_argument(
        "-p",
        "--pipeline",
        type=str,
        help="The stage of the job to run",
        default="all",
        choices=[
            "all",
            "get_seeds",
            "fuzz",
            "summarize",
        ],
    )
    parser.add_argument(
        "-ft", "--fuzztime", type=str, help="Time to fuzz one program", default="1d"
    )

    args = parser.parse_args()

    dataset = None
    if args.dataset == "FFmpeg":
        dataset = FFmpeg(seeds_dir="seeds")
    elif args.dataset == "qemu":
        dataset = Qemu(seeds_dir="seeds")
    else:
        unreachable("No dataset provided.")

    def convert_to_seconds(s: str) -> int:
        seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
        return int(s[:-1]) * seconds_per_unit[s[-1]]

    if args.pipeline == "all":
        dataset.get_seeds()
        dataset.fuzz(jobs=args.jobs, timeout=convert_to_seconds(args.fuzztime))
    elif args.pipeline == "get_seeds":
        dataset.get_seeds()
    elif args.pipeline == "fuzz":
        dataset.fuzz(jobs=args.jobs, timeout=convert_to_seconds(args.fuzztime))
    else:
        unreachable("Unkown pipeline provided")


# main function
if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    main()
