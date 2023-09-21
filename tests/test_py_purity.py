# type: ignore

import unittest
from scripts.source_code import py_use_global_variable, is_py_primitive_type
import logging


class TestGetParamsPy(unittest.TestCase):
    def test_py_global(self):
        code = "def addX(y):\n    z = x + y\n    return z"
        self.assertTrue(py_use_global_variable(code, "addX"))

        code = "def addX(y):\n    return x + y"
        self.assertTrue(py_use_global_variable(code, "addX"))

        code = "def add(x, y):\n    return x + y"
        self.assertFalse(py_use_global_variable(code, "add"))

    def test_py_primitive(self):
        value = "1"
        self.assertTrue(is_py_primitive_type(value))

        value = "None"
        self.assertTrue(is_py_primitive_type(value))

        value = "{'encoding': None, 'confidence': 0.0, 'language': None}"
        self.assertTrue(is_py_primitive_type(value))

        value = "<chardet.universaldetector.UniversalDetector object at 0x7fe01f73ac10>"
        self.assertFalse(is_py_primitive_type(value))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
