import os
import json
import re
import docker
from logging import error, info, warning
import cpp_demangle
import argparse
from typing import Optional
from common import *


# Extract specific function
def extract_func_code(
    func_name: str, code_content: str, if_c_code: bool
) -> Optional[str]:
    ori_func_name = func_name
    # Transliteration special characterss, replace special characters with \ ahead of themselves
    pattern = r"[\[\].,{}()\W_]"
    func_name = re.sub(pattern, r"\\\g<0>", func_name)
    # If C code, there is no demangle process, only have function name
    # Thus manually add parphsis to match the function
    if if_c_code:
        # Searching string that start with anything followed with function name+()+{
        # In the re it should not have any ; > <
        match_func_init = re.search(
            f"(?:\n|.*){func_name}\s*\([^;><]*\)(?:\s*|\n)\\{{\n", code_content
        )
    else:
        match_func_init = re.search(f".*{func_name}[^;]*\n", code_content)
    # If found matched function
    if match_func_init:
        # The regular expression end with {\n, thus I need to move ahead three char to get the full function namespace.
        func_init, func_start = match_func_init.group(), match_func_init.end() - 3
    else:
        warning(f" No match function {ori_func_name} found")
        return None
    # Match braces to get function code
    func_now, open_braces, flag = func_start, 0, 1
    while (open_braces > 0 or flag) and func_now < len(code_content):
        if code_content[func_now] == "{":
            open_braces += 1
            flag = 0
        elif code_content[func_now] == "}":
            open_braces -= 1
        func_now += 1
    # The matching is incorrect
    if open_braces > 0:
        warning(f" Malformed function definition for '{ori_func_name}' in code file")
        return None
    # Return code content
    function_code = code_content[func_start:func_now]
    return func_init + function_code


# get source code from docker
def get_source_from_docker(
    file_path: str, file_name: str, proj_name: str
) -> Optional[str]:
    # Create a container from the image
    client = docker.from_env()
    image = client.images.get(f"gcr.io/oss-fuzz/{proj_name}:latest")
    container = client.containers.run(image, detach=True)
    # check file_path, it may not the absolute path
    if "/" not in file_path or file_path[0] != "/":
        file_path = os.path.join("/src", proj_name, file_path)
    try:
        code_content = ""
        for chunk in container.get_archive(file_path)[0]:
            code_content += chunk.decode("utf-8")
    except docker.errors.NotFound:
        code_content = None
        error(f" File  {file_path}  NOT found\n")
    # Stop and remove the container
    container.stop()
    container.remove()
    return code_content


def main(proj_name: str):
    json_path = os.path.join(OSSFUZZ_SCRIPTS_HOME, "dump", proj_name)
    json_file_names = [f for f in os.listdir(json_path) if f.endswith(".json")]
    info(f"Looking for json file: {json_file_names}")

    for json_file_name in json_file_names:
        file_name = json_file_name.split(".json")[0]
        # open Json file and get filename+func_name
        with open(os.path.join(json_path, json_file_name), "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                warning(f" {json_file_name}  Json file illegal")
                continue
        info(f"NUMBER OF FUNCTION: {len(data)}")
        pre_file_path, code_content = "", ""
        for cnt in range(len(data)):
            file_func_name = ""
            for file_func_name_ in data[cnt]:
                file_func_name = file_func_name_

            # if split not matched, need to add a check
            splited_file_func_name = file_func_name.split(FILE_FUNC_DELIM)
            file_path, mangle_func_name = (
                splited_file_func_name[0],
                splited_file_func_name[1],
            )
            # if this is c file then the mangle does not exist
            try:
                demangle_func_name = cpp_demangle.demangle(mangle_func_name)
            except ValueError:
                demangle_func_name = mangle_func_name

            if demangle_func_name == None:  # mangle_func_name == demangle_func_name
                warning(f" {mangle_func_name} demangle incorrect or unable to demangle")
                data[cnt][
                    file_func_name
                ] = f" {mangle_func_name}demangle incorrect or unable to demangle"
            else:
                func_name = demangle_func_name.split("(")[0]
                # Try to get code_content, the json file may provide the path or not
                # only get code when pre_file_path!=file_path
                if pre_file_path != file_path:
                    code_content = get_source_from_docker(
                        file_path, file_name, proj_name
                    )
                    pre_file_path = file_path
                    info(f"Open source file: {pre_file_path}")
                    output_path = os.path.join(
                        OSSFUZZ_SCRIPTS_HOME, "output", proj_name
                    )
                    if not os.path.exists(output_path):
                        os.mkdir(output_path)
                    # If code_content is not None, then write to file
                    if code_content:
                        with open(f"{output_path}/{json_file_name}.txt", "w") as fi:
                            # write to JSON file
                            fi.write(code_content)
                if code_content == None:
                    error(f"{json_file_name} CODE content ERROR")
                    pre_file_path = f"try again {cnt}"
                    continue
                extrac_func_content = extract_func_code(func_name, code_content, True)
                func_content = (
                    "func extract error"
                    if extrac_func_content is None
                    else extrac_func_content
                )
                # write to json
                data[cnt][file_func_name] = {
                    "code": func_content,
                    "data": data[cnt][file_func_name],
                }
        # open the file for writing
        with open(
            os.path.join(OSSFUZZ_SCRIPTS_HOME, "output", proj_name, json_file_name), "w"
        ) as json_file:
            # write to JSON file
            json.dump(data, json_file)


# main function
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Catch source code")
    parser.add_argument(
        "-n",
        "--name",
        type=str,
        required=False,
        default="coturn",
        help="The project name to fetch",
    )
    args = parser.parse_args()
    main(args.name)
