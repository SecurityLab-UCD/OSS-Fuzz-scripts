import unittest
from scripts.source_code import c_get_params
import logging


class TestGetParamsC(unittest.TestCase):
    def test_c_parameter_list(self):
        code = "int add(int x, int y) { return x + y; }"
        params = c_get_params(code)

        self.assertEqual(params, [("int", "x"), ("int", "y")])

    def test_c_no_param(self):
        code = "void do_nothing() { return; }"
        params = c_get_params(code)

        self.assertEqual(params, [])

    def test_c_not_func_decl(self):
        code = "int x = 5;"
        params = c_get_params(code)
        self.assertIsNone(params)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
