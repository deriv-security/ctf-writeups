#include <stdio.h>
#include <string.h>
#include <unistd.h>

int readln(char *buf, size_t size) {
    int n = read(0, buf, size - 1);
    if (n <= 0) {
        return n;
    }
    if (buf[n - 1] == 10) {
        buf[n - 1] = 0;
    } else {
        buf[n] = 0;
    }
    return n;
}

int main(void) {
    char buf[96];
    int n = readln(buf, 96);
    int new = strnlen(buf, 0x60);
    printf("size: 0x%x", new);
    return 0;
}