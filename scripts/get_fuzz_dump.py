import os
import argparse
import logging

from scripts.projects import Project


def get_fuzz_dump(project: str, max_fuzz_time: int = 1800) -> None:
    dataset = Project(project, "fuzz", "dump")
    time = 45
    build_dir = os.path.join("./oss-fuzz/build/out", project)
    dump_dir = os.path.join("./dump", project)
    fuzz_dir = os.path.join("./fuzz", project)
    # Total binaries to be fuzzed
    targets = [
        f
        for f in os.listdir(build_dir)
        if not os.path.isdir(os.path.join(build_dir, f))
        and f != "llvm-symbolizer"
        and "." not in f
    ]
    total_binaries = len(targets)

    lowest_time_fail = None
    longest_time_success = 0

    # Remove files that will be replaced when fuzzing
    os.system(f"rm -f {dump_dir}/*")
    os.system(f"rm -rf {fuzz_dir}/timeout*")
    os.system(f"rm -rf {fuzz_dir}/crashes/*")
    os.system(f"rm -rf {build_dir}/timeout*")

    while True:
        # Fuzz target
        # os.system(
        #     "python3 ./scripts/projects.py -d {} -p fuzz_w_pass -ft {}s".format(
        #         project, time
        #     )
        # )
        dataset.fuzz(jobs=int(os.environ.get("CORES")), fuzztime=time, dump=True)

        # Count number of json files
        num_files_dumped = 0
        for path in os.listdir(dump_dir):
            if path[len(path) - 5 : len(path)] == ".json":
                num_files_dumped += 1
        print(f"Dumped: {num_files_dumped} out of {total_binaries} files")

        if num_files_dumped < total_binaries:
            lowest_time_fail = time
            new_time = int((lowest_time_fail + longest_time_success) / 2)
            if (
                new_time <= longest_time_success
                or lowest_time_fail
                and new_time >= lowest_time_fail
            ):
                break
            time = new_time
        else:
            longest_time_success = time
            new_time = (
                int((lowest_time_fail + longest_time_success) / 2)
                if lowest_time_fail is not None
                else longest_time_success * 2
            )
            if (
                lowest_time_fail
                and new_time >= lowest_time_fail
                or new_time <= longest_time_success
            ):
                break
            time = new_time

        # Remove files that will be replaced when fuzzing again
        os.system(f"rm -f {dump_dir}/*")
        os.system(f"rm -rf {fuzz_dir}/timeout*")
        os.system(f"rm -rf {fuzz_dir}/crashes/*")
        os.system(f"rm -rf {build_dir}/timeout*")

        if time >= max_fuzz_time or time < 1:
            break

    # Remove files that will be replaced when fuzzing again
    os.system(f"rm -f {dump_dir}/*")
    os.system(f"rm -rf {fuzz_dir}/timeout*")
    os.system(f"rm -rf {fuzz_dir}/crashes/*")
    os.system(f"rm -rf {build_dir}/timeout*")
    # os.system(
    #     "python3 ./scripts/projects.py -d {} -p fuzz_w_pass -ft {}s".format(
    #         project, longest_time_success
    #     )
    # )
    if longest_time_success > 0:
        # Fuzz again with the longest time that still dumps all of the json files
        dataset.fuzz(
            jobs=int(os.environ.get("CORES")), fuzztime=longest_time_success, dump=True
        )

        print(f"Done fuzzing {project} for {longest_time_success} seconds")
    else:
        print(f"{project} fuzzing cannot dump for every binary, fuzzing for one second")
        # Fuzz again for one second
        dataset.fuzz(jobs=int(os.environ.get("CORES")), fuzztime=1, dump=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=str, help="The project to fuzz")

    args = parser.parse_args()

    get_fuzz_dump(args.project)


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    main()

