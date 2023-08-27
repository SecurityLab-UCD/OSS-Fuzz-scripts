import json
from scripts.func_data import FunctionData, FunctionDataJSONEncoder
import os
from os import path
import argparse
import logging


def main(args):
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
    file_paths = []
    match args.mode:
        case "file":
            file_paths.append(args.path)
        case "dir":
            for root, dirs, fs in os.walk(args.path):
                for f in fs:
                    if f.endswith(".json"):
                        file_paths.append(path.join(root, f))

    for file_path in file_paths:
        try:
            with open(f"{file_path}", "r") as f:
                all_function_data = json.load(f)
                postprocessed_function_data = []
                for func in all_function_data:
                    func_name = list(func.keys())[0]
                    postprocessed_function_data.append(
                        FunctionData(file_func_name=func_name, **func[func_name])
                    )
            # Remove the file extension
            file_name = os.path.splitext(file_path)[0]
            with open(f"{file_name}.postprocessed.json", "w") as f:
                json.dump(postprocessed_function_data, f, cls=FunctionDataJSONEncoder)
        except Exception as e:
            logging.error(f"Error processing {file_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="old_to_new.py",
        description="convert old dump format to new dump format",
    )
    parser.add_argument(
        "--mode", "-m", type=str, default="file", choices=["file", "dir"]
    )
    parser.add_argument(
        "--path",
        "-p",
        type=str,
        default="fuzz_example.json",
        help="path to file or dir to convert",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    main(args)
