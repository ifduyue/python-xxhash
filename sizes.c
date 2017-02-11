#include <stdio.h>
#include <limits.h>
#include <unistd.h>             /* For the ssize_t header */
 
int main(void)
{
    printf("\n\nSigned    : Size %22s %22s\n", "Min", "Max");
    printf
        ("--------------------------------------------------------------\n");
    printf("char      : %4d %22d %22d\n", (int) sizeof(char), CHAR_MIN,
           CHAR_MAX);
    printf("short     : %4d %22d %22d\n", (int) sizeof(short), SHRT_MIN,
           SHRT_MAX);
    printf("int       : %4d %22d %22d\n", (int) sizeof(int), INT_MIN,
           INT_MAX);
    printf("long      : %4d %22ld %22ld\n", (int) sizeof(long), LONG_MIN,
           LONG_MAX);
    printf("long long : %4d %22lld %22lld\n\n", (int) sizeof(long long),
           LLONG_MIN, LLONG_MAX);
 
    printf("Unsigned  : Size %22s %22s\n", "Min", "Max");
    printf
        ("--------------------------------------------------------------\n");
    printf("char      : %4d %22d %22u\n", (int) sizeof(unsigned char), 0,
           UCHAR_MAX);
    printf("short     : %4d %22d %22u\n", (int) sizeof(unsigned short), 0,
           USHRT_MAX);
    printf("int       : %4d %22d %22u\n", (int) sizeof(unsigned int), 0,
           UINT_MAX);
    printf("long      : %4d %22d %22lu\n", (int) sizeof(unsigned long), 0,
           ULONG_MAX);
    printf("long long : %4d %22d %22llu\n\n",
           (int) sizeof(unsigned long long), 0, ULLONG_MAX);
 
    printf("Miscellaneous sizes:\n");
    printf
        ("--------------------------------------------------------------\n");
 
    printf("Single precision float: %38d\n", (int) sizeof(float));
    printf("Double precision float: %38d\n", (int) sizeof(double));
    printf("size_t: %54d\n", (int) sizeof(size_t));
    printf("ssize_t: %53d\n", (int) sizeof(ssize_t));
 
    return 0;
}
