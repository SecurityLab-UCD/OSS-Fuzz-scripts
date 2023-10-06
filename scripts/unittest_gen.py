def to_cpp_GoogleTest(func_name: str, io_pairs: list[list[list[str]]]) -> str:
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


def to_py_unittest(
    func_name: str, io_pairs: list[list[list[str]]], param_list: list[str]
) -> str:
    from py_io_capture import PythonReportError

    is_class_method = False
    match func_name.split("."):
        case [function_name]:
            decl = f"def test_{func_name}():"
        case [class_name, function_name]:
            decl = f"def test_{class_name}_{function_name}():"
            is_class_method = True
            func_name = function_name
        case _:
            decl = f"def test_{func_name}():"

    lines = [decl]
    for io in io_pairs:
        inputs = io[0]
        # replace optional parameters to format: param_name=optional_value
        if PythonReportError.OPTIONAL_ARG_ABSENT in inputs:
            start_idx = inputs.index(PythonReportError.OPTIONAL_ARG_ABSENT)
            n_params = len(param_list)
            # todo: in some case, reported inputs is more than param_list
            # to reproduce: run postprocess on chardet/__init__.py?detect
            for i in range(start_idx, n_params):
                if inputs[i] != PythonReportError.OPTIONAL_ARG_ABSENT:
                    inputs[i] = f"{param_list[i]}={inputs[i]}"
            # since optional parameters are converted to keyword arguments,
            # we can filter out all OPTIONAL_ARG_ABSENT
            inputs = [
                val
                for val in inputs[:n_params]
                if val != PythonReportError.OPTIONAL_ARG_ABSENT
            ]

        outputss = io[1]
        if is_class_method:
            obj_init = inputs[0]
            real = f"{obj_init}.{func_name}({', '.join(inputs[1:])})"
        else:
            real = f"{func_name}({', '.join(inputs)})"

        # todo: consider optional parameters
        # idx 0 is the actual rnt value, the rest are pointer inputs
        expected_outputs = [outputs[0] for outputs in outputss if len(outputs) > 0]
        if (
            all(expected_outputs[0] == output for output in expected_outputs)
            or is_class_method  # if is class method, we only consider the first output with instance init constructor
        ):
            # all expected outputs are the same
            expected = expected_outputs[0] if len(expected_outputs) > 0 else "None"
            lines.append(f"    assert {real} == {expected}")
        else:
            # todo: decide how to handle different expected outputs
            pass

    return "\n".join(lines)
