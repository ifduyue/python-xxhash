from __future__ import print_function
import sys
import ctypes

print("sys.maxint             =", sys.maxint)
print("sys.long_info          =", sys.long_info)
print("sys.float_info         =", sys.float_info)

print("ctypes.c_uint(-1)      =", ctypes.c_uint(-1))
print("ctypes.c_ulonglong(-1) =", ctypes.c_ulonglong(-1))

print("2 ** 32 - 1            = %d" % (2 ** 32 - 1))
print("-1 & (2 ** 32 - 1)     = %d" % (-1 & (2 ** 32 - 1)))

print("2 ** 64 - 1            = %d" % (2 ** 64 - 1))
print("-1 & (2 ** 64 - 1)     = %d" % (-1 & (2 ** 64 - 1)))
