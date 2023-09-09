import unittest
from scripts.unittest_gen import UNITTEST_GENERATOR
import logging


class TestSourceCodePy(unittest.TestCase):
    def test_cpp_GoogleTest(self):
        func_name = "foo"
        io_pairs = [[["1", "2"], [["3"], ["4"]]]]
        to_unittest = UNITTEST_GENERATOR["cpp"]

        expected = "#include <gtest/gtest.h>\nTEST(FOO_TEST, FOO) {\n  EXPECTED_EQ(foo(1, 2), 3);\n  EXPECTED_EQ(foo(1, 2), 4);\n}"
        self.assertEqual(to_unittest(func_name, io_pairs), expected)

    def test_cpp_GoogleTest_multiple_outputs(self):
        func_name = "foo"
        io_pairs = [[["1", "2"], [["3", "5"]]]]
        to_unittest = UNITTEST_GENERATOR["cpp"]

        expected = "#include <gtest/gtest.h>\nTEST(FOO_TEST, FOO) {\n  EXPECTED_EQ(foo(1, 2), 3);\n}"
        self.assertEqual(to_unittest(func_name, io_pairs), expected)

    def test_cpp_GoogleTest_no_return(self):
        func_name = "foo"
        io_pairs = [[["1", "2"], [[]]]]
        to_unittest = UNITTEST_GENERATOR["cpp"]

        expected = "#include <gtest/gtest.h>\nTEST(FOO_TEST, FOO) {\n}"
        self.assertEqual(to_unittest(func_name, io_pairs), expected)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
