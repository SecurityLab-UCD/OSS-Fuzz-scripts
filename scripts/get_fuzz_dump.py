from os import path
import os
import argparse

def directories(project: str) -> None:
    build_dir = os.path.join("./oss-fuzz/build/out", project)
    dump_dir = os.path.join("./dump", project)
    fuzz_dir = os.path.join("./fuzz", project)

    print("Build Directory: {}".format(build_dir))
    print(os.listdir(build_dir))
    print("Dump Directory: {}".format(dump_dir))
    print(os.listdir(dump_dir))
    print("Fuzz Directory: {}".format(fuzz_dir))
    print(os.listdir(fuzz_dir))

def get_fuzz_dump(project: str) -> None: 
    time = 45
    build_dir = os.path.join("./oss-fuzz/build/out", project)
    dump_dir = os.path.join("./dump", project)
    fuzz_dir = os.path.join("./fuzz", project)
    # Total binaries to be fuzzed
    targets = [
        f
        for f in os.listdir(build_dir)
        if not os.path.isdir(os.path.join(build_dir, f)) and f != "llvm-symbolizer" and '.' not in f
    ]
    total_binaries = len(targets)

    lowest_time_fail = None
    longest_time_success = 0

    os.system("rm -f " + dump_dir + "/*")
    os.system("rm -rf " + fuzz_dir + "/timeout*")
    os.system("rm -rf " + build_dir + "/timeout*")
    
    while True:
        # Fuzz target
        os.system(
            "python3 ./scripts/projects.py -d {} -p fuzz_w_pass -ft {}s".format(
                project, time
            )
        )

        # Count number of json files
        num_files_dumped = 0
        for path in os.listdir(dump_dir):
            if path[len(path) - 5 : len(path)] == ".json":
                num_files_dumped += 1
        print("Dumped: {} out of {} files".format(num_files_dumped, total_binaries))
        # Max fuzz time of 1800 seconds for now
        if longest_time_success >= 1800:
            break
        elif num_files_dumped < total_binaries:
            lowest_time_fail = time
            new_time = int((lowest_time_fail + longest_time_success) / 2)
            if new_time <= longest_time_success or lowest_time_fail and new_time >= lowest_time_fail:
                break
            time = new_time
        else:
            longest_time_success = time
            new_time = int((lowest_time_fail + longest_time_success) / 2) if lowest_time_fail is not None else longest_time_success * 2 
            if lowest_time_fail and new_time >= lowest_time_fail or new_time <= longest_time_success:
                break
            time = new_time

        # Remove dump files and timeout files
        os.system("rm -f " + dump_dir + "/*")
        os.system("rm -rf " + fuzz_dir + "/timeout*")
        os.system("rm -rf " + build_dir + "/timeout*")
        
        # Max fuzz time of 1800 seconds for now
        if time >= 1800:
            break

    # Fuzz again with the longest time that still dumps all of the json files
    os.system("rm -f " + dump_dir + "/*")
    os.system("rm -rf " + fuzz_dir + "/timeout*")
    os.system("rm -rf " + build_dir + "/timeout*")
    os.system(
        "python3 ./scripts/projects.py -d {} -p fuzz_w_pass -ft {}s".format(
            project, longest_time_success
        )
    )
    print("Done fuzzing {} for {} seconds.".format(project, longest_time_success))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=str, help="The dataset to fuzz")

    args = parser.parse_args()

    project = args.dataset

    get_fuzz_dump(project)


if __name__ == "__main__":
    main()
