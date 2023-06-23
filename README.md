# OSS-Fuzz-scripts

scripts for building func-io datasets on [oss-fuzz](https://github.com/google/oss-fuzz) supported open-source projects.

## Requirements

- [python3.8](https://www.python.org/downloads/release/python-380/) or above
- [docker](https://docs.docker.com/engine/install/ubuntu/)
- [clang+llvm14](https://github.com/llvm/llvm-project/), our [init script](./scripts/init.sh) will get this for you.

## Setup

```sh
source ./scripts/env.sh
./scripts/init.sh
```

## Building Dataset

```bash
python3 scripts/projects.py -d <project> -p build_w_pass
python3 scripts/projects.py -d <project> -p fuzz_w_pass -ft 1s
```

where `<project>` can be chose from [build_w_pass.md](./built_w_pass.md).

## ToDo

We are working on C/C++ projects first since thet have the most fuzzer targets.
The next step is to extend this project to Python and Java since
these two languages are also widely used in LLM code-understanding tasks.
