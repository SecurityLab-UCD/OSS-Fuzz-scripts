import unittest
from source_code import py_get_func_code_demangled
import logging


class TestSourceCodePy(unittest.TestCase):
    def test_py_regular(self):
        usage = py_get_func_code_demangled("../tests/app.py", "usage", None)
        self.assertIsNotNone(usage)
        logging.info(usage)

    def test_py_defined_inclass(self):
        wants = py_get_func_code_demangled(
            "../tests/app.py", "wants", "ExceptionHandler"
        )
        self.assertIsNotNone(wants)
        logging.info(wants)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
