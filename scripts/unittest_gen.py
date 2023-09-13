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
        for outputs in outputss:
            if len(outputs) > 0:
                # idx 0 is the actual rnt value, the rest are pointer inputs
                expected = outputs[0]
                lines.append(f"  EXPECTED_EQ({real}, {expected});")
            else:
                # no return, then the expect return is void
                # ASSERT_TRUE((std::is_same<decltype(MyFunction()), void>::value));
                # https://stackoverflow.com/questions/69036412/assert-with-googletest-that-a-function-does-not-return-a-value-void
                continue
    lines.append("}")
    return "\n".join(lines)


UNITTEST_GENERATOR = {
    "c": to_cpp_GoogleTest,
    "cpp": to_cpp_GoogleTest,
    "cxx": to_cpp_GoogleTest,
    "cc": to_cpp_GoogleTest,
}
