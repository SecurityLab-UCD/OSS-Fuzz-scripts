s = '__ZN5Eigen15DenseCoeffsBaseINS_6MatrixINSt3__17complexIdEELin1ELi1ELi0ELin1ELi1EEELi1EEixEl'

import os
import json
import glob
import re
import ctypes

import cpp_demangle

# a mangled C++ symbol name
mangled_name = s#'_ZNSt3__16vectorIiNS_9allocatorIiEEEED2Ev'

# demangle the symbol name
demangled_name = cpp_demangle.demangle(mangled_name)

# print the demangled name
print(demangled_name)

# def demangle12(func: str):
#     # Load the C++ Standard Library
#     libcxx = ctypes.cdll.LoadLibrary("libc++.so.1")
#     # Define the signature of the __cxa_demangle() function
#     demangle = libcxx.__cxa_demangle
#     demangle.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_int)]
#     # Call __cxa_demangle() to demangle the input string
#     output_buffer = ctypes.create_string_buffer(256)
#     output_size = ctypes.c_size_t(256)
#     status = ctypes.c_int(0)

#     result = demangle(func.encode(), output_buffer, ctypes.byref(output_size), ctypes.byref(status))
    
#     # Forced return demangle value
#     return output_buffer.value.decode('utf-8')
# print(demangle12(s))