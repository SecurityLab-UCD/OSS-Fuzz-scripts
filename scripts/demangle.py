import os
import json
import glob
import re
import docker
import ctypes
from logging import error, info, warning
import cpp_demangle
import argparse
from typing import Optional, Union
from common import OSSFUZZ_SCRIPTS_HOME


def extract_func_code(
    func_name: str, code_content: str, if_c_code: bool
) -> Optional[str]:
    # Transliteration special characters
    ori_func_name = func_name
    pattern = r"[\[\].,{}()\W_]"
    # Replace special characters with \ ahead of themselves
    func_name = re.sub(pattern, r"\\\g<0>", func_name)
    # If C code, there is no parphsis in the func_name, so it need to manually add it
    if if_c_code:
        match_func_init = re.search(
            f"(?:.*\n|.*){func_name}\s*\([^;]*\)(?:\s*|\n)\\{{\n", code_content
        )
    else:
        match_func_init = re.search(f".*{func_name}[^;]*\n", code_content)
    # Found match
    if match_func_init:
        # The regular expression end with {\n, thus I need to move ahead three char to get the full function namespace.
        func_init, func_start = match_func_init.group(), match_func_init.end() - 3
    else:
        warning(f" No match function {ori_func_name} found")
        return ""

    func_now, open_braces, flag = func_start, 0, 1

    while (open_braces > 0 or flag) and func_now < len(code_content):
        if code_content[func_now] == "{":
            open_braces += 1
            flag = 0
        elif code_content[func_now] == "}":
            open_braces -= 1
        func_now += 1

    if open_braces > 0:
        warning(f" Malformed function definition for '{ori_func_name}' in code file")
        return ""

    function_code = code_content[func_start:func_now]
    return func_init + function_code


def demangle_func(func: str) -> Optional[str]:
    # Load the C++ Standard Library
    libcxx = ctypes.cdll.LoadLibrary("libc++.so.1")
    # Define the signature of the __cxa_demangle() function
    demangle = libcxx.__cxa_demangle
    demangle.argtypes = [
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.POINTER(ctypes.c_int),
    ]
    # Call __cxa_demangle() to demangle the input string
    output_buffer = ctypes.create_string_buffer(256)
    output_size = ctypes.c_size_t(256)
    status = ctypes.c_int(0)
    result = demangle(
        func.encode(), output_buffer, ctypes.byref(output_size), ctypes.byref(status)
    )
    # Forced return demangle value
    return output_buffer.value.decode("utf-8")
    # if result == 0:
    #     # Demangling was successful
    #     demangled_name = output_buffer.value.decode('utf-8')
    #     return demangled_name
    # else:
    #     # Demangling failed
    #     print("Demangling failed with status", status)


# get source code from docker
def get_source_from_docker(
    file_path: str, file_name: str, proj_name: str
) -> Optional[str]:
    # Create a container from the image
    client = docker.from_env()
    image = client.images.get("gcr.io/oss-fuzz/" + proj_name + ":latest")
    container = client.containers.run(image, detach=True)
    # check file_path, it may not the absolut path
    if not "/" in file_path:
        file_path = "/src/" + proj_name + "/" + file_path
    try:
        code_content = ""
        for chunk in container.get_archive(file_path)[0]:
            code_content += chunk.decode("utf-8")
    except docker.errors.NotFound:
        code_content = "ERROR"
        error(f" File  {file_path}  NOT found\n")
    # Stop and remove the container
    container.stop()
    container.remove()
    return code_content


def main():
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
    proj_name = args.name
    json_path = os.path.join(OSSFUZZ_SCRIPTS_HOME, "dump", proj_name)
    json_file_names = [f for f in os.listdir(json_path) if f.endswith(".json")]
    info(f"Looking for json file: {json_file_names}")

    for json_file_name in json_file_names:
        file_name = json_file_name.split(".json")[0]
        # open Json file and get filename + func_name
        with open(json_path + "/" + json_file_name, "r") as f:
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
            splited_file_func_name = file_func_name.split("?")
            file_path, mangle_func_name = (
                splited_file_func_name[0],
                splited_file_func_name[1],
            )
            # if this is c file then the mangle does not exist
            try:
                demangle_func_name = cpp_demangle.demangle(mangle_func_name)
            except ValueError:
                demangle_func_name = mangle_func_name

            if demangle_func_name == "":  # mangle_func_name == demangle_func_name
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
                    if not os.path.exists(f"./output/{proj_name}/"):
                        os.mkdir(f"./output/{proj_name}/")
                    with open(f"./output/{proj_name}/{json_file_name}.txt", "w") as fi:
                        # write to JSON file
                        fi.write(code_content)
                if code_content == "ERROR" or code_content == "":
                    error(f"{json_file_name} CODE content ERROR")
                    pre_file_path = f"try again {cnt}"
                    continue
                func_content = extract_func_code(func_name, code_content, True)
                # write to json
                data[cnt][file_func_name] = {
                    "code": func_content,
                    "data": data[cnt][file_func_name],
                }
        # open the file for writing
        with open("./output/" + proj_name + "/" + json_file_name, "w") as json_file:
            # write to JSON file
            json.dump(data, json_file)


# main function
if __name__ == "__main__":
    main()
