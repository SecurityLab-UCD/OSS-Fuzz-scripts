import os
import json
import re
import docker
import tarfile
import io
from logging import error, info, warning
import cpp_demangle
import argparse
from typing import Optional
from common import *
from source_code import *


# Get all files from docker
def copy_files_from_docker(proj_name: str, output_path: str) -> bool:
    """
    Get all target project files from docker

    Args:
        proj_name (str): Target project name.
        output_path (str): The local path to store the files.

    Returns:
        bool: True if the copying was successful, False otherwise.
    """
    client = docker.from_env()
    image = client.images.get(f"gcr.io/oss-fuzz/{proj_name}:latest")
    container = client.containers.run(image, detach=True)
    try:
        stream, _ = container.get_archive("/src")
    except docker.errors.NotFound:
        error(f"Docker  {proj_name} path /src  NOT found\n")
        return False

    fileobj = io.BytesIO()
    for chunk in stream:
        fileobj.write(chunk)
    fileobj.seek(0)

    # Extract files from the file-like object
    with tarfile.open(fileobj=fileobj) as tar:
        tar.extractall(output_path)

    container.stop()
    container.remove()
    return True


def get_source_code_path(suffix_file_path: str, output_path: str) -> Optional[str]:
    """
    Match and get target file path from local

    Args:
        suffix_file_path (str): Suffix path of target file.
        output_path (str): The path of project.

    Returns:
        str: target source code file path.
    """
    # Transliteration special characterss, replace special characters with \ ahead of themselves
    pattern = r"[\[\].,{}()\W_]"
    suffix_file_path = re.sub(pattern, r"\\\g<0>", suffix_file_path)

    pattern = f".*{suffix_file_path}$"
    regex = re.compile(pattern)

    for root, directories, files in os.walk(output_path):
        for file in files:
            file_path = os.path.join(root, file)
            if regex.match(file_path):
                return file_path
    return None


def main(proj_name: str, proj_language: str = "c"):
    json_path = os.path.join(OSSFUZZ_SCRIPTS_HOME, "dump", proj_name)
    output_path = os.path.join(OSSFUZZ_SCRIPTS_HOME, "output", proj_name, "codes")
    # Get all files from docker
    if not copy_files_from_docker(proj_name, output_path):
        error(f"Fetch {proj_name} source code failed")
        return
    json_file_names = [f for f in os.listdir(json_path) if f.endswith(".json")]
    info(f"Looking for json file: {json_file_names}")

    for json_file_name in json_file_names:
        file_name = os.path.splitext(json_file_name)[0]
        # open Json file and get filename+func_name
        with open(os.path.join(json_path, json_file_name), "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                warning(f" {json_file_name}  Json file illegal")
                continue
        info(f"NUMBER OF FUNCTION: {len(data)}")
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
            if demangle_func_name == None:
                warning(f" {mangle_func_name} demangle incorrect or unable to demangle")
                data[cnt][
                    file_func_name
                ] = f" {mangle_func_name}demangle incorrect or unable to demangle"
            else:
                func_name = demangle_func_name.split("(")[0]
                # Get code path from local
                code_path = get_source_code_path(file_path, output_path)
                if code_path == None:
                    warning(f"Get source code path error {file_path}")
                    data[cnt][file_func_name] = {
                        "code": None,
                        "data": data[cnt][file_func_name],
                    }
                    continue
                # get function content check project languages
                if proj_language == "c" or proj_language == "cpp":
                    func_content = clang_get_func_code(code_path, func_name)
                elif proj_language == "python":
                    # class_name need to defined in json file
                    func_content = inspect_get_func_code_demangled(
                        code_path, func_name, class_name=None
                    )
                # write to json
                data[cnt][file_func_name] = {
                    "code": func_content,
                    "data": data[cnt][file_func_name],
                }
        # write back to JSON
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
    parser.add_argument(
        "-l",
        "--language",
        type=str,
        required=False,
        default="c",
        help="The project language",
    )
    args = parser.parse_args()
    main(args.name, args.language)
