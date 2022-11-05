# 🚀Typedef-Generator🚀
Typedef-Generator - a tool to generate typedef's from C++ function prototypes

# Usage🔍
    > t_gen.py [c++ file] [postfix] [default calling convention]

# Example✍️
## myfunctions.h
```c++
const char* test(unsigned int* first_arg);
```
	> t_gen.py myfunctions.h _t __fastcall

Result:
```c++
typedef const char *(__fastcall* test_t)(unsigned int * first_arg);
```

# Remarks☝️
* Some include chains might not be resolved, all unknown types will be replaced with int then
* For parsing WinApi files, add #include <windows.h> at the top of the file, this will help to resolve types
* Also, some preprocessor directives can screw this script up a bit
* You can use findstr/grep to extract needed function's typedef from file
