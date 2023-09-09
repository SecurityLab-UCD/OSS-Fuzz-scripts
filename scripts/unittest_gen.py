def to_cpp_GoogleTest(func_name: str, io_pairs: list[list[str]]) -> str:
    lines = []
    testcase_name = func_name.upper() + "_TEST"
    test_name = func_name.upper()

    # todo: inlcude dependency libraries
    lines.append("#include <gtest/gtest.h>")
    lines.append("TEST(" + testcase_name + ", " + test_name + ") {")

    for io in io_pairs:
        inputs = io[0]
        outputss = io[1]
        real = f"{func_name}({', '.join(inputs)})"
        for outputs in outputss:
            expected = ", ".join(outputs)
            lines.append(f"  EXPECTED_EQ({real}, {expected});")
    lines.append("}")
    return "\n".join(lines)


UNITTEST_GENERATOR = {
    "c": to_cpp_GoogleTest,
    "cpp": to_cpp_GoogleTest,
    "cxx": to_cpp_GoogleTest,
    "cc": to_cpp_GoogleTest,
}
