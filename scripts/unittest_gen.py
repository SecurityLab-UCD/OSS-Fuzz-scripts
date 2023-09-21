def to_cpp_GoogleTest(func_name: str, io_pairs: list[list[str]]) -> str:
    lines = []
    testcase_name = func_name.upper() + "_TEST"
    test_name = func_name.upper()

    # todo: include dependency libraries
    lines.append("#include <gtest/gtest.h>")
    lines.append("TEST(" + testcase_name + ", " + test_name + ") {")

    for io in io_pairs:
        inputs = io[0]
        outputss = io[1]
        real = f"{func_name}({', '.join(inputs)})"

        # idx 0 is the actual rnt value, the rest are pointer inputs
        expected_outputs = [outputs[0] for outputs in outputss if len(outputs) > 0]
        # todo: no return, then the expect return is void
        # ASSERT_TRUE((std::is_same<decltype(MyFunction()), void>::value));
        # https://stackoverflow.com/questions/69036412/assert-with-googletest-that-a-function-does-not-return-a-value-void

        if all(expected_outputs[0] == output for output in expected_outputs):
            # all expected outputs are the same
            expected = expected_outputs[0]
            lines.append(f"  ASSERT_EQ({real}, {expected});")
        else:
            # todo: decide how to handle different expected outputs
            pass

    lines.append("}")
    return "\n".join(lines)


def to_py_unittest(func_name: str, io_pairs: list[list[str]]) -> str:
    match func_name.split("."):
        case [function_name]:
            decl = f"def test_{func_name}():"
        case [class_name, function_name]:
            decl = f"def test_{class_name}_{function_name}():"
        case _:
            decl = f"def test_{func_name}():"

    lines = [decl]
    for io in io_pairs:
        inputs = io[0]
        outputss = io[1]
        real = f"{func_name}({', '.join(inputs)})"

        # todo: consider optional parameters
        # idx 0 is the actual rnt value, the rest are pointer inputs
        expected_outputs = [outputs[0] for outputs in outputss if len(outputs) > 0]
        if all(expected_outputs[0] == output for output in expected_outputs):
            # all expected outputs are the same
            expected = expected_outputs[0]
            lines.append(f"    assert {real} == {expected}")
        else:
            # todo: decide how to handle different expected outputs
            pass

    return "\n".join(lines)


UNITTEST_GENERATOR = {
    "c": to_cpp_GoogleTest,
    "cpp": to_cpp_GoogleTest,
    "cxx": to_cpp_GoogleTest,
    "cc": to_cpp_GoogleTest,
    "python": to_py_unittest,
}
