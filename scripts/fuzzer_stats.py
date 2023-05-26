import pandas as pd


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
            delim (str): demiliter used to split function name from fuzzer name
        """
        self.name = name
        self.stats = []
        for d in json_dump:
            for key in d:
                io_pirs = d[key]
                summarize_dict = {}
                func = key.split(delim)[1]
                summarize_dict["project"] = project
                summarize_dict["language"] = lang
                summarize_dict["fuzzer"] = self.name
                summarize_dict["function"] = func
                summarize_dict["unique_inputs"] = len(io_pirs)
                summarize_dict["total_executions"] = sum(
                    map(lambda x: len(x[1]), io_pirs)
                )
                self.stats.append(summarize_dict)

    def __iter__(self):
        return iter(self.stats)


def summarize_fuzzer_stats_df(df: pd.DataFrame):
    print(
        f"""
        Number of unique functions executed in the dataset: {df.function.nunique()}
        Number of unique inputs: {df.unique_inputs.sum()}
        Number of total IO pairs: {df.total_executions.sum()}
    """
    )
