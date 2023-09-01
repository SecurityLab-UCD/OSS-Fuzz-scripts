from common import *
from os import path
import os
from typing import List, Tuple
from logging import error, info, warning

import json
import pandas as pd
from scripts.util import (
    oss_fuzz_one_target,
    concatMap,
)
from scripts.fuzzer_stats import FuzzerStats, summarize_fuzzer_stats_df


class Project:
    def __init__(self, project: str, fuzzdir: str, dumpdir: str, config: dict):
        self.project = project
        self.fuzzdir = path.join(OSSFUZZ_SCRIPTS_HOME, fuzzdir)
        self.dumpdir = path.join(OSSFUZZ_SCRIPTS_HOME, dumpdir)
        self.proj_fuzzout = path.join(self.fuzzdir, self.project)
        self.proj_dumpout = path.join(self.dumpdir, self.project)
        self.targets: List[str] = []
        self.project_oss_dir = path.join(OSSFUZZ, "projects", self.project)
        self.file_func_delim = FILE_FUNC_DELIM
        self.config = config

    def build(self):
        if self.config["language"] == "python":
            os.system(
                f"python3 {OSSFUZZ}/infra/helper.py build_fuzzers {self.project} --sanitizer coverage --clean"
            )
        else:
            os.system(
                f"python3 {OSSFUZZ}/infra/helper.py build_fuzzers {self.project} --sanitizer none --clean"
            )
        self._update_targets()

    def mkdir_if_doesnt_exist(self):
        if not path.isdir(self.fuzzdir):
            os.makedirs(self.fuzzdir)

        if not path.isdir(self.proj_fuzzout):
            os.makedirs(self.proj_fuzzout)

        if not path.isdir(self.dumpdir):
            os.makedirs(self.dumpdir)

        if not path.isdir(self.proj_dumpout):
            os.makedirs(self.proj_dumpout)

        proj_crash = path.join(self.proj_fuzzout, "crashes")
        if not path.isdir(proj_crash):
            os.makedirs(proj_crash)

        for t in self.targets:
            fuzz_subdir = path.join(self.proj_fuzzout, str(t))
            if not path.isdir(fuzz_subdir):
                os.makedirs(fuzz_subdir)

    def _update_targets(self):
        bindir = path.join(OSSFUZZ, "build/out", self.project)
        if not path.isdir(bindir):
            warning("project build dir doesn't exist, please build the project first")

        # since each projects has its own style of naming fuzzers
        #   w/o fuzzer as substring of fuzzer names
        # and some language projects's fuzzers are not exec
        #   for example, jvm projects have -rwxr--r-- Log4jFuzzer
        # we will just take any file thats not a directory
        # if any of collected files is not actually a fuzzer, the result corpus dir will be just empty
        self.targets = [
            f
            for f in os.listdir(bindir)
            if not path.isdir(path.join(bindir, f)) and f != "llvm-symbolizer"
        ]

    def fuzz(self, jobs=CORES, fuzztime=3600, dump=False):
        if not self.targets:
            self._update_targets()

        if not self.targets:
            warning("no targets found, please build fuzzers first")

        self.mkdir_if_doesnt_exist()

        info("Collecting binaries to fuzz")
        bins_to_fuzz: List[Tuple[str, str, str | None]] = []
        for t in self.targets:
            if "." in t:
                continue
            fuzzout = path.join(self.fuzzdir, self.project, t)
            dumpout = t + ".json" if dump else None
            bins_to_fuzz.append((t, fuzzout, dumpout))

        info(f"Fuzzing all {len(bins_to_fuzz)} binaries for {fuzztime} seconds")
        parallel_subprocess(
            bins_to_fuzz,
            jobs,
            lambda r: oss_fuzz_one_target(r, proj=self.project, fuzztime=fuzztime),
            on_exit=None,
        )

        # redirect all crashes
        crash_dir = path.join(self.fuzzdir, self.project, "crashes")
        outfiles = os.listdir(f"{OSSFUZZ}/build/out/{self.project}")
        if any([f.startswith("crash-") for f in outfiles]):
            os.system(f"mv {OSSFUZZ}/build/out/{self.project}/crash-* {crash_dir}")
        # redirect all timeouts
        timeout_dir = path.join(self.fuzzdir, self.project, "timeout")
        if any([f.startswith("timeout-") for f in outfiles]):
            os.system(f"mv {OSSFUZZ}/build/out/{self.project}/timeout-* {timeout_dir}")

        # redirect all dumps from oss-fuzz workdir
        if dump:
            dump_dir = path.join(self.dumpdir, self.project)
            outfiles = os.listdir(f"{OSSFUZZ}/build/out/{self.project}")
            if any([f.endswith(".json") for f in outfiles]):
                os.system(f"mv {OSSFUZZ}/build/out/{self.project}/*.json {dump_dir}")

    def get_project_stats(self) -> pd.DataFrame:
        def analyze_fuzzer(fname: str) -> FuzzerStats:
            dumpfile = path.join(self.proj_dumpout, fname)
            fuzzer = fname.split(".json")[0]
            with open(dumpfile, "r") as f:
                data = json.load(f)
            return FuzzerStats(
                self.project,
                self.config["language"],
                fuzzer,
                data,
                self.file_func_delim,
            )

        summaries_for_all_fuzzers: Iterable[FuzzerStats] = concatMap(
            analyze_fuzzer, os.listdir(self.proj_dumpout)
        )

        return pd.DataFrame(list(summaries_for_all_fuzzers))

    def summarize(self):
        df = self.get_project_stats()
        summarize_fuzzer_stats_df(df)

    def _is_auto_supported(self):
        lang = self.config["language"]
        supported_langs = ["c", "cpp", "c++", "jvm"]
        return lang.lower() in supported_langs

    def postprocess(self):
        import scripts.demangle as ossfuzz_demangle

        proj_name = self.project
        ossfuzz_demangle.main(proj_name, self.config["language"])

    def build_w_pass(self, build_script: str = "build_w_pass.sh"):
        raise NotImplementedError

    def auto_build_w_pass(self, cpp: str):
        raise NotImplementedError
