
#include <stdio.h>
#include <stdlib.h>

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

  return 0;
}