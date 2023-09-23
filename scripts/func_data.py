import json
from enum import IntEnum
from typing import Optional
from scripts.source_code import (
    c_get_params,
    is_c_primitive_type,
    is_py_primitive_type,
    c_use_global_variable,
    py_use_global_variable,
    py_get_params,
)
from scripts.unittest_gen import to_cpp_GoogleTest, to_py_unittest


class SourceCodeStatus(IntEnum):
    SUCCESS = 1  # Found source code
    TEMPLATE = 2  # Template function (only applicable for C++ source code)
    NOT_FOUND = 3  # Couldn't find source code
    DEMANGLE_ERROR = 4  # Could be TEMPLATE or NOT_FOUND, couldn't demangle to check
    PATH_ERROR = 5  # Source code path specified in JSON file could not be found


class FunctionData:
    def __init__(
        self,
        file_func_name: str,
        language: str,
        code=None,
        status=None,
        data=None,
    ) -> None:
        """Class that contains function data to dump to json"""
        self.file_func_name = file_func_name
        self.language = language
        self.code = code
        self.status = status
        self.data = data

    @staticmethod
    def stringify_one_iopair(
        io: list[list[str]], io_delim="#", output_delim=";", val_delim="<SEP>"
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
        self, io_delim="#", output_delim=";", val_delim="<SEP>"
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
            "only_primitive_parameter": self.only_primitive_parameter(),
            "use_global": self.use_global(),
            "unittest": self.to_unittest(),
        }

    def only_primitive_parameter(self) -> bool | None:
        match self.language:
            case "c" | "cpp" | "cxx" | "cc":
                if self.code is None:
                    return None
                match c_get_params(self.code):
                    case None:
                        return None
                    case param_list:
                        return all(map(lambda x: is_c_primitive_type(x[0]), param_list))
            case "python":
                # if no input/output data, we consider it as void
                if self.data is None:
                    return True

                def is_io_primitive(io: list[list[str]]) -> bool:
                    values_to_check = io[0]  # inputs
                    if len(io[1]) > 0:
                        values_to_check += io[1][0]  # outputs (return value)
                    return all(map(is_py_primitive_type, values_to_check))

                return all(map(is_io_primitive, self.data))

            case _:
                return None

    def use_global(self) -> bool | None:
        if self.code is None:
            return None

        match self.language:
            case "c" | "cpp" | "cxx" | "cc":
                return c_use_global_variable(self.code)
            case "python":
                return py_use_global_variable(self.code)
            case _:
                return None

    def to_unittest(self) -> str | None:
        """Generate unittest for this function

        Returns:
            str: unittest code for this function from fuzz io pairs
        """
        _, func_name = self.file_func_name.split("?")
        if self.data is None:
            return None

        match self.language:
            case "c" | "cpp" | "cxx" | "cc":
                return to_cpp_GoogleTest(func_name, self.data)
            case "python":
                if self.code is None:
                    return None
                param_list = py_get_params(self.code)
                return to_py_unittest(func_name, self.data, param_list)
            case _:
                return None


class FunctionDataJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, FunctionData):
            return o.to_stringified_dict()
        return json.JSONEncoder.default(self, o)
