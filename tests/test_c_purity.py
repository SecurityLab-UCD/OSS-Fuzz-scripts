# type: ignore

import unittest
from scripts.source_code import c_get_params, is_c_primitive_type, c_use_global_variable
import logging
from clang.cindex import TypeKind as CTypeKind


class TestGetParamsC(unittest.TestCase):
    def test_c_parameter_list(self):
        code = "int add(int x, int y) { return x + y; }"
        params = c_get_params(code)

        self.assertEqual(params, [(CTypeKind.INT, "x"), (CTypeKind.INT, "y")])
        if params is not None:
            for param in params:
                self.assertTrue(is_c_primitive_type(param[0]))

    def test_c_no_param(self):
        code = "void do_nothing() { return; }"
        params = c_get_params(code)

        self.assertEqual(params, [])

    def test_c_not_func_decl(self):
        code = "int x = 5;"
        params = c_get_params(code)
        self.assertIsNone(params)

    def test_c_global(self):
        code = "int addX(int y) { int z = x + y; return z; } "
        self.assertTrue(c_use_global_variable(code))

        code = "int addX(int y) { return x + y; } "
        self.assertTrue(c_use_global_variable(code))

        code = "int add(int x, int y) { return x + y; }"
        self.assertFalse(c_use_global_variable(code))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
