import os
import json
import re
import docker
from logging import error, info, warning
import cpp_demangle
import argparse
from typing import Optional
from common import *
from source_code import *


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
        # Hard coding possible file path to retrive file
        file_path4 = "/src"
        file_path3 = os.path.join("/src", file_path)
        file_path2 = os.path.join("/src", proj_name, "src", file_path)
        file_path = os.path.join("/src", proj_name, file_path)

        build_sh = ""
        for chunk in container.get_archive("/src/build.sh")[0]:
            build_sh += chunk.decode("utf-8")
        pattern = r"cd\s+(\S+)"
        matches = re.findall(pattern, build_sh)
        for match in matches:
            file_path4 = os.path.join(file_path4, match)

    # Try those possible path
    try:
        code_content = ""

        for chunk in container.get_archive(file_path)[0]:
            code_content += chunk.decode("utf-8")
    except docker.errors.NotFound:
        try:
            code_content = ""
            for chunk in container.get_archive(file_path2)[0]:
                code_content += chunk.decode("utf-8")
        except docker.errors.NotFound:
            try:
                code_content = ""
                for chunk in container.get_archive(file_path3)[0]:
                    code_content += chunk.decode("utf-8")
            except docker.errors.NotFound:
                try:
                    code_content = ""
                    for chunk in container.get_archive(file_path4)[0]:
                        code_content += chunk.decode("utf-8")
                except docker.errors.NotFound:
                    code_content = None
                    error(f"File  {file_path}  NOT found\n")
    # Stop and remove the container
    container.stop()
    container.remove()
    return code_content


def main(proj_name: str):
    json_path = os.path.join(OSSFUZZ_SCRIPTS_HOME, "dump", proj_name)
    json_file_names = [f for f in os.listdir(json_path) if f.endswith(".json")]
    code_list = []
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
        code_content = ""
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
                # Try to get code_content when the source code file haven't been retrived yet
                # TODO: featch all code_content in one time
                info(f"Open source file: {file_path}")
                output_path = os.path.join(
                    OSSFUZZ_SCRIPTS_HOME, "output", proj_name, "codes"
                )
                output_code_path = os.path.join(
                    output_path, os.path.basename(file_path)
                )
                # if current file have not been retrived, open docker to get it
                if file_path not in code_list:
                    code_content = get_source_from_docker(
                        file_path, file_name, proj_name
                    )
                    if not os.path.exists(output_path):
                        os.makedirs(output_path)
                    if code_content == None:
                        error(f"{file_path} CODE content ERROR")
                        continue
                    code_list.append(file_path)
                    with open(output_code_path, "w") as fi:
                        # write to .c file
                        fi.write(code_content)
                # get function content
                func_content = clang_get_func_code(output_code_path, func_name)
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
    args = parser.parse_args()
    main(args.name)
