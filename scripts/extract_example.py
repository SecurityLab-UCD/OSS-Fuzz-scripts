from source_code import *

# The input paramater need to modified before running
# Function defined in-class extraction example
func_inclass = inspect_get_func_code_demangled(
    "/home/hxxzhang/OSS-Fuzz-scripts/output/abseil-py/codes/abseil-py/absl/app.py",
    "wants",
    "ExceptionHandler",
)
print(func_inclass)

# Function extraction example
func = inspect_get_func_code_demangled(
    "/home/hxxzhang/OSS-Fuzz-scripts/output/abseil-py/codes/abseil-py/absl/app.py",
    "usage",
    None,
)

print(func)
