
#include <stdlib.h>

int separate_decl_def(int a, int b);
int separate_decl_def(int a, int b) { return a + b; }

// clang-format off
int 
two_lines_def(int a, int b) {
  return a + b;
}

struct LinkedNode {
  int value;
  struct LinkedNode *next;
};

struct 
LinkedNode 
*create_list(int n) {
  struct LinkedNode *head = NULL;
  for (int i = 0; i < n; i++) {
    struct LinkedNode *node =
        (struct LinkedNode *)malloc(sizeof(struct LinkedNode));
    node->value = i;
    node->next = head;
    head = node;
  }
  return head;
}

// clang-format on
void *json_parse_string(const char *string) {
  if (string == NULL)
    return NULL;
  // SKIP_WHITESPACES(&string);
  if (*string != '{' && *string != '[')
    return NULL;
  return string;
}

int add(int a, int b) { return a + b; }

int main() { return 0; }