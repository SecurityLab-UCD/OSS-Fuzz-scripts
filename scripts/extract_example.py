from source_code import *

func_inclass = inspect_get_func_code_demangled(
    "/home/hxxzhang/OSS-Fuzz-scripts/output/abseil-py/codes/abseil-py/absl/app.py",
    "wants",
    "ExceptionHandler",
)
print(func_inclass)
func = inspect_get_func_code_demangled(
    "/home/hxxzhang/OSS-Fuzz-scripts/output/abseil-py/codes/abseil-py/absl/app.py",
    "usage",
    None,
)

print(func)
