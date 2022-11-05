import clang.cindex
import sys
import re


DEFAULT_CALLING_CONVENTIONS = [
    "__stdcall",
    "__fastcall",
    "__cdecl",
    "__vectorcall",
    "__thiscall",
    "__clrcall"
]

DECLSPEC_RE = "__declspec\(.*?\)"
EXTERN_C_RE = 'extern "C"'


# node filters
def filter_by_kind(nodes, kinds):
	return list(filter(lambda node: node.kind in kinds, nodes))

def filter_by_location(nodes, filenames):
	return list(filter(lambda node: node.location.file.name in filenames, nodes))


# converters/extractors
def get_calling_convention(function):
    result = ""
    tokens = list(function.get_tokens())
    i = 0
    for token in tokens:
        if token.spelling == '(':
            calling_convention = tokens[i - 2]
            if (calling_convention.kind == clang.cindex.TokenKind.KEYWORD):
                if (calling_convention.spelling in DEFAULT_CALLING_CONVENTIONS):
                    return calling_convention
            elif (calling_convention.kind == clang.cindex.TokenKind.IDENTIFIER) and (i > 2):
                return calling_convention
            return None
            break
            
        i += 1


# typedef return_type(calling_convention* name)(args);
def translate_to_typedef(function, postfix="_t", default_calling_convention="__cdecl"):
    calling_convention = get_calling_convention(function)
    if not calling_convention:
        calling_convention = default_calling_convention
    else:
        calling_convention = calling_convention.spelling
    
    
    args = "("
    
    args_list = list(function.get_arguments())
    arg_count = len(args_list)
    
    i = 0
    for arg in args_list:
        args += f"{arg.type.spelling} {arg.displayname}"
        if i != arg_count - 1:
            args += ", "
        i += 1
    
    args += ")"
    
    return f"typedef {function.result_type.spelling}({calling_convention}* {function.spelling}{postfix}){args};"

def remove_unhandled(line, regex, str):
    re.sub(regex, "", line)

    new_line = ""
    if line.startswith("#define") and (str in line.lower()):
        spaces = 0
        for i in line:
            if i == ' ':
                spaces += 1
                
            if spaces >= 2:
                break
            
            new_line += i
        new_line += "\n"
    else:
        return line
    
    return new_line

def main(argv):
    if len(argv) < 4:
        print(f"usage: {argv[0]} [c++ file] [postfix] [default calling convention]")
        print(f"T-Gen - a tool to generate typedef's from C++ function prototype\n")
        print("Example:")
        print(f"myfunctions.h:")
        print("const char* test(unsigned int* first_arg);\n")
        print(f"> {argv[0]} myfunctions.h _t __fastcall")
        print(f"typedef const char *(__fastcall* test_t)(unsigned int * first_arg);\n")
        print("Some include chains might not be resolved, all unknown types will be replaced with int then")
        print("For parsing WinApi files, add #include <windows.h> at the top of the file, this will help to resolve types")
        print("Also, some preprocessor directives can screw this script up a bit")
        print("You can use findstr/grep to extract needed function's typedef from file")
        return

    index = clang.cindex.Index.create()
    
    tmp = ""
    with open(argv[1], "r") as file:
        for line in file:
            line = remove_unhandled(line, DECLSPEC_RE, "declspec").replace('extern "C" {', '/*extern "C" {*/')
            tmp += remove_unhandled(line, EXTERN_C_RE, 'extern "c"')
        
    translation_unit = index.parse(argv[1], args=["-x", "c++", "-std=c++17"],
                                    unsaved_files=[(argv[1], tmp)])
 
    functions = filter_by_kind(translation_unit.cursor.get_children(), [clang.cindex.CursorKind.FUNCTION_DECL])
    functions = filter_by_location(functions, [argv[1]])

    for function in functions:
        print(translate_to_typedef(function, argv[2], argv[3]))
  

if __name__ == "__main__":
    main(sys.argv)