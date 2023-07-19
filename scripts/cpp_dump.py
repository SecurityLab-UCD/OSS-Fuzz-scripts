from os import path
import os
import argparse

from analyze import get_proj_info
from get_fuzz_dump import get_fuzz_dump, directories

def build_and_fuzz(option: str) -> None: 
    # Get all C++ projects
    with open("./built_w_pass.md", "r") as f:
        lines = f.readlines()
    projects = [
        info[0]
        for info in [get_proj_info(line) for line in lines]
        if info is not None and info[1] == "c++"
    ]
    # These projects weren't auto built
    projects.remove("ffmpeg")
    projects.remove("llvm")
    projects.remove("libpng")

    for project in projects:
        dump_dir = os.path.join("./dump", project)
        # If continue, check if dump directory has json files already
        if option == 'c' and os.path.exists(dump_dir) and len(os.listdir(dump_dir)) > 0:
            continue
        else:
            # Delete previous dump if want to build and fuzz all projects
            if option == 'a':
                os.system("rm -rf {}".format(dump_dir))

            # Build and fuzz project
            os.system(
                "python3 ./scripts/projects.py -d {} -p auto_build_w_pass --cpp=c++".format(
                    project
                )
            )
            print("Done building {}".format(project))
            get_fuzz_dump(project)
            print("Done fuzzing {}".format(project))



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("option", type=str, help="Options: a(ll), c(ontinue)")

    args = parser.parse_args()

    option = args.option.lower()

    # Run build and fuzz
    if option == 'a' or option == "all":
        build_and_fuzz('a')
    elif option == 'c' or option == "continue":
        build_and_fuzz('c')
    else:
        print("Options: a(ll), c(ontinue)")
        exit(1)

if __name__ == "__main__":
    main()
