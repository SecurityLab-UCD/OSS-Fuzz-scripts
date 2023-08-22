import pandas as pd
from typing import List, Tuple


class FuzzerStats:
    def __init__(
        self, project: str, lang: str, name: str, json_dump: dict, delim: str
    ) -> None:
        """Iterable class that contains stats of a fuzzer

        Args:
            project (str): name of project
            lang (str): language of project
            name (str): name of fuzzer
            json_dump (dict): result of running Project.fuzz_w_pass()
            delim (str): delimiter used to split function name from fuzzer name
        """
        self.name = name
        self.stats = []
        for d in json_dump:
            for key in d:
                io_pairs = d[key]
                summarize_dict = {}
                func = key.split(delim)[1]
                summarize_dict["project"] = project
                summarize_dict["language"] = lang
                summarize_dict["fuzzer"] = self.name
                summarize_dict["function"] = func
                summarize_dict["deterministic"] = is_deterministic(io_pairs)
                summarize_dict["unique_inputs"] = len(io_pairs)
                summarize_dict["total_executions"] = sum(
                    map(lambda x: len(x[1]), io_pairs)
                )
                self.stats.append(summarize_dict)

    def __iter__(self):
        return iter(self.stats)


def is_deterministic(io_pairs: List[Tuple[str, List[str]]]) -> bool:
    """check if function io pairs are deterministic

    Args:
        io_pairs (List[Tuple[str, List[str]]): list of io pairs, each input corresponds to a list of outputs

    Returns:
        bool: True if deterministic, False otherwise
    """
    
    # in report, each input corresponds to a hash_set of outputs
    # so if the function is deterministic, each input should correspond to a hash_set of size 1
    return all(map(lambda x: len(x[1]) == 1, io_pairs))


def summarize_fuzzer_stats_df(df: pd.DataFrame):
    print(
        f"""
        Number of unique functions executed in the dataset: {df.function.nunique()},
        Number of deterministic functions: {df.groupby('function')['deterministic'].all().sum()},
        Number of unique inputs: {df.unique_inputs.sum()}
        Number of total IO pairs: {df.total_executions.sum()}
    """
    )
