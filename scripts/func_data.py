import json
from enum import IntEnum


class SourceCodeStatus(IntEnum):
    SUCCESS = 1  # Found source code
    TEMPLATE = 2  # Template function (only applicable for C++ source code)
    NOT_FOUND = 3  # Couldn't find source code
    DEMANGLE_ERROR = 4  # Could be TEMPLATE or NOT_FOUND, couldn't demangle to check
    PATH_ERROR = 5  # Source code path specified in JSON file could not be found


class FunctionData:
    def __init__(self, file_func_name, code=None, status=None, data=None) -> None:
        """Class that contains function data to dump to json"""
        self.file_func_name = file_func_name
        self.code = code
        self.status = status
        self.data = data

    @staticmethod
    def stringify_one_iopair(
        io: list[list[str]], io_delim="#", output_delim=";", val_delim=","
    ) -> str:
        """Stringify one io pair reporting

        Args:
            io (list[list[str]]): one execution's fuzz data [inputs, [outputs]]
            io_delim (str, optional): delimiter for inputs and outputs. Defaults to "#".
            output_delim (str, optional): delimiter for each outputs list. Defaults to ";".
            val_delim (str, optional): delimiter for each value. Defaults to ",".

        Returns:
            str: stringified fuzz data for one io pair, e.g. "1,2,3#1,2;3,4"
        """
        inputs = io[0]
        outputss = io[1]
        inputs_str = val_delim.join(inputs)
        outputs_str = output_delim.join(
            [val_delim.join(outputs) for outputs in outputss]
        )
        return f"{inputs_str}{io_delim}{outputs_str}"

    def to_stringified_dict(
        self, io_delim="#", output_delim=";", val_delim=","
    ) -> dict:
        """__dict__ but "data" is stringified

        Args:
            io_delim (str, optional): delimiter for inputs and outputs. Defaults to "#".
            output_delim (str, optional): delimiter for each outputs list. Defaults to ";".
            val_delim (str, optional): delimiter for each value. Defaults to ",".

        Returns:
            dict: dict that "data" is stringified
        """
        return {
            "file_func_name": self.file_func_name,
            "code": self.code,
            "status": self.status,
            "data": [
                self.stringify_one_iopair(exec, io_delim, output_delim, val_delim)
                for exec in self.data
            ]
            if self.data is not None
            else None,
        }


class FunctionDataJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, FunctionData):
            return o.to_stringified_dict()
        return json.JSONEncoder.default(self, o)
