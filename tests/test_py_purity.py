# type: ignore

import unittest
from scripts.source_code import (
    py_use_global_variable,
    is_py_primitive_type,
    py_get_params,
)
import logging


class TestGetParamsPy(unittest.TestCase):
    def test_py_global(self):
        code = "def addX(y):\n    z = x + y\n    return z"
        self.assertTrue(py_use_global_variable(code))

        code = "def addX(y):\n    return x + y"
        self.assertTrue(py_use_global_variable(code))

        code = "def add(x, y):\n    return x + y"
        self.assertFalse(py_use_global_variable(code))

        code = "def add(x, y):\n    z = x + y\n    return z"
        self.assertFalse(py_use_global_variable(code))

        code = "def foo(x, y):\n    z = 1\n    return z"
        self.assertFalse(py_use_global_variable(code))

        code = "def boo(x, y):\n    z = x\n    return z"
        self.assertFalse(py_use_global_variable(code))

        code = "def int_from_bytes(value, signed=False):\n    return int.from_bytes(value, 'big', signed=signed)"
        self.assertFalse(py_use_global_variable(code))

    def test_py_primitive(self):
        value = "1"
        self.assertTrue(is_py_primitive_type(value))

        value = "None"
        self.assertTrue(is_py_primitive_type(value))

        value = "{'encoding': None, 'confidence': 0.0, 'language': None}"
        self.assertTrue(is_py_primitive_type(value))

        value = "<chardet.universaldetector.UniversalDetector object at 0x7fe01f73ac10>"
        self.assertFalse(is_py_primitive_type(value))

    def test_py_get_param(self):
        code = "def addX(y):\n    z = x + y\n    return z"
        self.assertEqual(py_get_params(code), ["y"])

        code = "def add(x, y):\n    return x + y"
        self.assertEqual(py_get_params(code), ["x", "y"])

        code = "def add(x: int, y: int):\n    return x + y"
        self.assertEqual(py_get_params(code), ["x", "y"])

    def test_py_get_param_optional(self):
        code = "def add(x, y=3):\n    return x + y"
        self.assertEqual(py_get_params(code), ["x", "y"])

        code = "def add(x: int=1, y: int=2):\n    return x + y"
        self.assertEqual(py_get_params(code), ["x", "y"])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
