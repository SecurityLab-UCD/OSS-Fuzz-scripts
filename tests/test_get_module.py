import unittest
from scripts.source_code import py_get_imported_modules
import logging
from os import path


class TestGetImportedModules(unittest.TestCase):
    def test_import(self):
        code = "import datetime"
        modules = py_get_imported_modules(code)
        self.assertEqual(modules, ["datetime"])

        code = "import datetime\nimport os"
        modules = py_get_imported_modules(code)
        self.assertEqual(modules, ["datetime", "os"])

    def test_from_import(self):
        code = "from datetime import datetime"
        modules = py_get_imported_modules(code)
        self.assertEqual(modules, ["datetime"])

        code = "from os import path"
        modules = py_get_imported_modules(code)
        self.assertEqual(modules, ["path"])

        code = "from collections import defaultdict, namedtuple"
        modules = py_get_imported_modules(code)
        self.assertEqual(modules, ["defaultdict", "namedtuple"])

    def test_from_import_w_dot(self):
        code = "from scripts.source_code import py_get_imported_modules"
        modules = py_get_imported_modules(code)
        self.assertEqual(modules, ["py_get_imported_modules"])

    def test_import_alias(self):
        code = "import numpy as np"
        modules = py_get_imported_modules(code)
        self.assertEqual(modules, ["np"])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
