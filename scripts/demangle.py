import os
import json
import glob
import re
import ctypes

json_path = '../dump/augeas'
proj_path = '../oss-fuzz/projects/augeas'
file_names = [f for f in os.listdir(json_path) if f.endswith('.json') and os.path.isfile(json_path+'/'+f)]
print('Looking for json file: ',file_names)
def extract_func_code(func_name, file_path):
    with open(file_path, 'r') as file:
        code_content = file.read()
    # init regular expression
    match_func_init = re.search(".*"+func_name,code_content)
    if match_func_init:
        func_init, func_start = match_func_init.group(), match_func_init.end()
    else:
        #raise ValueError(f"No match found")
        print(f"ERROR: No match function '{func_name}' found")
        return f"ERROR: No match function '{func_name}' found"
    
    func_now, open_braces, flag = func_start, 0, 1

    while (open_braces > 0 or flag) and func_now < len(code_content):
        if code_content[func_now] == "{":
            open_braces += 1
            flag=0
        elif code_content[func_now] == "}":
            open_braces -= 1
        func_now += 1

    if open_braces > 0: # raise ValueError(f"Malformed function definition for '{func_name}' in code file")
        print(f"ERROR: Malformed function definition for '{func_name}' in code file")
        return f"ERROR: Malformed function definition for '{func_name}' in code file"

    function_code = code_content[func_start:func_now]
    return func_init+function_code

def demangle(func: str):
    # Load the C++ Standard Library
    libcxx = ctypes.cdll.LoadLibrary("libc++.so.1")

    # Define the signature of the __cxa_demangle() function
    demangle = libcxx.__cxa_demangle
    demangle.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_int)]
    # Call __cxa_demangle() to demangle the input string
    output_buffer = ctypes.create_string_buffer(256)
    output_size = ctypes.c_size_t(256)
    status = ctypes.c_int(0)
    result = demangle(func.encode(), output_buffer, ctypes.byref(output_size), ctypes.byref(status))
    # Forced return demangle value
    return output_buffer.value.decode('utf-8')
    # if result == 0:
    #     # Demangling was successful
    #     demangled_name = output_buffer.value.decode('utf-8')
    #     return demangled_name
    # else:
    #     # Demangling failed
    #     print("Demangling failed with status", status)

for json_file_name in file_names:
    file_name = json_file_name.split('.json')[0]
    # Find file path
    if len(glob.glob(proj_path+'/'+file_name+'.c*'))==0:
        print('ERROR: File '+proj_path+'/'+file_name+'.c*'+" NOT found")
        continue
    file_path = glob.glob(proj_path+'/'+file_name+'.c*')[0]
    # if file_name == 'augeas_api_fuzzer': continue
    # open Json file and get filename + func name
    with open(json_path+'/'+json_file_name, 'r') as f:
        try:
            data = json.load(f)
        except:
            try:
                # the json file start with path, reopen the json file
                with open(json_path+'/'+json_file_name, 'r') as f:
                    json_content,flag ='',0
                    for line in f:
                        if flag:
                            json_content+=line
                        elif line[0]=='{':
                            json_content+=line
                            flag=1
                    data = json.loads(json_content)
            except:
                print('ERROR: ',json_file_name, "Json file illegal")
                continue
    for file_func_name in data:
        # if split not matched, need to add a check
        mangle_func_name = file_func_name.split(file_name)
        if len(mangle_func_name)<2:
            raise ValueError(f"ERROR: File '{file_name}' not found, may open wrong json file")
        else:
            mangle_func_name = mangle_func_name[1]
            demangle_func_name = demangle(mangle_func_name)
            # Add a check demangle is correct?
            if mangle_func_name == demangle_func_name or demangle_func_name=='':
                print('ERROR: '+mangle_func_name+' demangle incorrect or unable to demangle')
            else:
                func_name = demangle_func_name.split('(')[0]
                # print('looking for func ', func_name, ' in  file ', file_path)
                func_content = extract_func_code(func_name,file_path)
                print(func_content)
