import unittest
from scripts.source_code import clang_get_func_code_mangled
import logging

TEST_FILE = "tests/mangle_example.cpp"


class TestSourceCodeCpp(unittest.TestCase):
    def test_overload_basic(self):
        mangled_foo1 = "_Z3fooii"
        mangled_foo2 = "_Z3fooi"

        foo1 = clang_get_func_code_mangled(TEST_FILE, mangled_foo1)
        self.assertIsNotNone(foo1)

        foo2 = clang_get_func_code_mangled(TEST_FILE, mangled_foo2)
        self.assertIsNotNone(foo2)
        self.assertNotEqual(foo1, foo2)

        logging.info(foo1)
        logging.info(foo2)

    def test_overload_param_type(self):
        mangled_boo_int = "_Z3booi"
        mangled_boo_float = "_Z3boof"

        boo_int = clang_get_func_code_mangled(TEST_FILE, mangled_boo_int)
        self.assertIsNotNone(boo_int)

        boo_float = clang_get_func_code_mangled(TEST_FILE, mangled_boo_float)
        self.assertIsNotNone(boo_float)
        self.assertNotEqual(boo_int, boo_float)

        logging.info(boo_int)
        logging.info(boo_float)

    def test_overload_return_type(self):
        mangled_boo_double = "_Z3bood"
        mangled_boo_int = "_Z3booi"

        boo_double = clang_get_func_code_mangled(TEST_FILE, mangled_boo_double)
        self.assertIsNotNone(boo_double)

        boo_int = clang_get_func_code_mangled(TEST_FILE, mangled_boo_int)
        self.assertNotEqual(boo_double, boo_int)

        logging.info(boo_double)

    def test_template(self):
        mangled_template_int = "_Z5t_fooIiET_S0_S0_"
        mangled_template_double = "_Z5t_fooIdET_S0_S0_"

        template_int = clang_get_func_code_mangled(TEST_FILE, mangled_template_int)
        self.assertIsNone(template_int)

        template_double = clang_get_func_code_mangled(
            TEST_FILE, mangled_template_double
        )
        self.assertIsNone(template_double)

    def test_overload_inheritance(self):
        mangled_parent_foo = "_ZN6Parent3fooEv"
        mangled_child_foo = "_ZN5Child3fooEv"

        parent_foo = clang_get_func_code_mangled(TEST_FILE, mangled_parent_foo)
        self.assertIsNotNone(parent_foo)

        child_foo = clang_get_func_code_mangled(TEST_FILE, mangled_child_foo)
        self.assertIsNotNone(child_foo)
        self.assertNotEqual(parent_foo, child_foo)

        logging.info(parent_foo)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()

