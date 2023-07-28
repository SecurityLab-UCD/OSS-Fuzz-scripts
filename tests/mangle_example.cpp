
#include <stdio.h>
#include <stdlib.h>

class Parent {
  public:
    void foo() {
        printf("Parent Foo");
    }
};

class Child : public Parent {
  public:
    void foo() {
        printf("Child Foo");
    }
};

template <typename T> T t_foo(T x, T y) {
    return (x > y) ? x : y;
}

int foo(int x) { return x + 1; }

int foo(int x, int y) { return x + y; }

int boo(int x) { return x + 1; }
int boo(float x) { return x + 1; }
double boo(double x) { return x + 1; }

int main() {
  int x = foo(1);
  int y = foo(1, 2);
  printf("x = %d\n", x);
  printf("y = %d\n", y);

  int z = boo(1);
  float w_in = 1.0;
  int w = boo(w_in);
  printf("z = %d\n", z);
  printf("w = %d\n", w);

  double d = boo(1.0);
  printf("d = %f\n", d);

  printf("%d\n", t_foo<int>(5, 7));
  printf("%f\n", t_foo<double>(5.5, 7.25));

  Parent p = Parent();
  p.foo();

  Child c = Child();
  c.foo();

  return 0;
}
