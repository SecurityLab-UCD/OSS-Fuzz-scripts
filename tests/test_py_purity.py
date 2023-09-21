# type: ignore

import unittest
from scripts.source_code import py_use_global_variable
import logging


class TestGetParamsC(unittest.TestCase):
    def test_c_global(self):
        code = "def addX(y):\n    z = x + y\n    return z"
        self.assertTrue(py_use_global_variable(code, "addX"))

        code = "def addX(y):\n    return x + y"
        self.assertTrue(py_use_global_variable(code, "addX"))

        code = "def add(x, y):\n    return x + y"
        self.assertFalse(py_use_global_variable(code, "add"))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
