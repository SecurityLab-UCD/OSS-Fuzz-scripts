import json
from scripts.func_data import FunctionData, FunctionDataJSONEncoder
import os
from os import path


def main():
    """convert a json file from old format to new format which decrease one level of nesting and convert data to strings

    Old Format:
    [
        {
            "func_name1": {
                "code": "int func_name1(int a, int b) { return a + b; }",
                "status": "OK",
                "data": [
                    [
                        [["1", "2"], [["3"], ["4"]]],
                        [["2", "3"], [["5"], ["6"]]]
                    ]
                ]
            }
        },
    ]

    New Format:
    [
        {
            "file_func_name": "file_name#func_name",
            "code": "int func_name1(int a, int b) { return a + b; }",
            "status": "OK",
            "data": [
                "1,2#3;4",
                "2,3#5;6"
            ]
        },
    ]
    """
    file_name = "fuzz_example.json"
    with open(f"{file_name}", "r") as f:
        all_function_data = json.load(f)
        postprocessed_function_data = []
        for func in all_function_data:
            func_name = list(func.keys())[0]
            postprocessed_function_data.append(
                FunctionData(file_func_name=func_name, **func[func_name])
            )

    with open(f"postprocessed_{file_name}", "w") as f:
        json.dump(postprocessed_function_data, f, cls=FunctionDataJSONEncoder)


if __name__ == "__main__":
    main()
