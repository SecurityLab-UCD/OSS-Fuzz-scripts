import unittest
from scripts.source_code import clang_get_func_code
import logging


class TestStringMethods(unittest.TestCase):
    def test_c_regular(self):
        foo = clang_get_func_code("tests/weird_func_def.c", "some_func_not_defined")
        self.assertEqual(foo, None)

        add = clang_get_func_code("tests/weird_func_def.c", "add")
        self.assertIsNotNone(add)
        logging.info(add)

    def test_c_multi_line(self):
        two_line = clang_get_func_code("tests/weird_func_def.c", "two_lines_def")
        self.assertIsNotNone(two_line)
        logging.info(two_line)

        create_list = clang_get_func_code("tests/weird_func_def.c", "create_list")
        self.assertIsNotNone(create_list)
        logging.info(create_list)

    def test_c_multiple_curly_brackets(self):
        json_parse_string = clang_get_func_code(
            "tests/weird_func_def.c", "json_parse_string"
        )
        self.assertIsNotNone(json_parse_string)
        logging.info(json_parse_string)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
