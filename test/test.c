#include <stdio.h>
#include <windows.h>

int main() {
  int i;

  // Print numbers from 1 to 10
  for (i = 1; i <= 10; i++) {
    Sleep(500);
    printf("%d\n", i);
    fflush(stdout);
  }
  return 0;
}