import os
import json
import glob
import re
import docker
import ctypes
import cpp_demangle

proj_name = 'tmux'
json_path = '../dump/'+proj_name
json_file_names = [f for f in os.listdir(json_path) if f.endswith('.json')]
print('Looking for json file: ',json_file_names)
cnt=0

def extract_func_code(func_name, code_content, if_c_code=True):
    # init regular expression
    try:
        # Transliteration special characters
        ori_func_name=func_name
        pattern = r"[\[\].,{}()\W_]"
        # Replace special characters with \ ahead of themselves
        func_name = re.sub(pattern, r"\\\g<0>", func_name)
        # If C code, there is no parphsis in the func_name, so it need to manually add it
        if if_c_code:
            match_func_init = re.search(".*"+func_name+'[^;]*\).*\{\n',code_content)
        else:
            match_func_init = re.search(".*"+func_name+'[^;]*\n',code_content)
    except:
        print("The function ", ori_func_name, " can not use regression expression, ignore first")
        return f"ERROR: No match function '{ori_func_name}' found"
    if match_func_init:
        func_init, func_start = match_func_init.group(), match_func_init.end()-3
    else:
        #raise ValueError(f"No match found")
        print(f"ERROR: No match function '{ori_func_name}' found")
        return f"ERROR: No match function '{ori_func_name}' found"
    
    func_now, open_braces, flag = func_start, 0, 1

    while (open_braces > 0 or flag) and func_now < len(code_content):
        if code_content[func_now] == "{":
            open_braces += 1
            flag=0
        elif code_content[func_now] == "}":
            open_braces -= 1
        func_now += 1

    if open_braces > 0: # raise ValueError(f"Malformed function definition for '{func_name}' in code file")
        print(f"ERROR: Malformed function definition for '{ori_func_name}' in code file")
        return f"ERROR: Malformed function definition for '{ori_func_name}' in code file"

    function_code = code_content[func_start:func_now]
    return func_init+function_code

def demangle_func(func: str):
    # Load the C++ Standard Library
    libcxx = ctypes.cdll.LoadLibrary("libc++.so.1")
    # Define the signature of the __cxa_demangle() function
    demangle = libcxx.__cxa_demangle
    demangle.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_int)]
    # Call __cxa_demangle() to demangle the input string
    output_buffer = ctypes.create_string_buffer(256)
    output_size = ctypes.c_size_t(256)
    status = ctypes.c_int(0)
    if cnt>=66:
        print("PASS??")
    result = demangle(func.encode(), output_buffer, ctypes.byref(output_size), ctypes.byref(status))
    if cnt>=66:
        print("PASS???")
    # Forced return demangle value
    return output_buffer.value.decode('utf-8')
    # if result == 0:
    #     # Demangling was successful
    #     demangled_name = output_buffer.value.decode('utf-8')
    #     return demangled_name
    # else:
    #     # Demangling failed
    #     print("Demangling failed with status", status)

def get_source_code(file_path, file_name):
    # get source code from docker
    # # Create a container from the image
    client = docker.from_env()
    image = client.images.get('gcr.io/oss-fuzz/'+proj_name+':latest')
    container=client.containers.run(image,detach=True)
    # The docker does not support regular expression, brute force try

    #check file_path, it may not the absolut path
    if not '/' in file_path:
        file_path='/src/'+proj_name+'/'+file_path
    try:
        code_content = ''
        for chunk in container.get_archive(file_path)[0]:
            code_content+=chunk.decode('utf-8')
    except:
        code_content='ERROR'
        print('ERROR: File '+file_path+" NOT found")
        print()
    # try:
    #     # try .c file and json path first
    #     # print('looking source code in path:', file_path+'.c')
    #     #Todo list of名字 正则表达
    #     code_content = ''
    #     for chunk in container.get_archive(file_path+'.c')[0]:
    #         code_content+=chunk.decode('utf-8')
    # except:
    #     try: 
    #         # try .cc file and json path first
    #         # print('looking source code in path:', file_path+'.cc')
    #         code_content = ''
    #         for chunk in container.get_archive(file_path+'.cc')[0]:
    #             code_content+=chunk.decode('utf-8')
    #     except:
    #         try:
    #             # the .c and json file did not provide the path
    #             # print('looking source code in path:', '/src/'+proj_name+'/'+file_name+'.c')
    #             code_content = ''
    #             for chunk in container.get_archive('/src/'+proj_name+'/'+file_name+'.c')[0]:
    #                 code_content+=chunk.decode('utf-8')
    #         except:
    #             try:
    #                 # the .c and json file did not provide the path
    #                 # print('looking source code in path:', '/src/'+proj_name+'/'+file_name+'.cc')
    #                 code_content = ''
    #                 for chunk in container.get_archive('/src/'+proj_name+'/'+file_name+'.cc')[0]:
    #                     code_content+=chunk.decode('utf-8')
    #             except:
    #                 code_content='ERROR'
    #                 print('ERROR: File '+file_path+'.c*'+" NOT found")
    #                 print()
    # Stop and remove the container
    container.stop()
    container.remove()
    return code_content

for json_file_name in json_file_names:
    file_name = json_file_name.split('.json')[0]
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
    print('NUMBER OF FUNCTION: ',len(data))
    pre_file_path,code_content = '',''
    for cnt in range(len(data)):
        file_func_name = ''
        for file_func_name_ in data[cnt]:
            file_func_name=file_func_name_
        if cnt>0 and cnt%100==0:
            print('DONE function',cnt,' ',file_func_name)
        
        # if split not matched, need to add a check
        splited_file_func_name = file_func_name.split('?')
        if len(splited_file_func_name)<2:
            print(f"ERROR: file_func_name->'{file_func_name}' in '{file_name}'.json file incorrect can not split")
            continue
        else:
            file_path,mangle_func_name=splited_file_func_name[0],splited_file_func_name[1]
            # for i in splited_file_func_name:
            #     if flag and '/' in i:
            #         file_path.append(i)
            #     else:
            #         flag=0
            #         mangle_func_name.append(i)
            # file_path = (file_name).join(file_path)+file_name
            # mangle_func_name = (file_name).join(mangle_func_name)
            # demangle mangle_func_name
            # demangle_func_name = demangle_func(mangle_func_name)
            # if this is c file then the mangle does not exist
            try:
                demangle_func_name = cpp_demangle.demangle(mangle_func_name)
            except:
                demangle_func_name = mangle_func_name
            
            if demangle_func_name=='': # mangle_func_name == demangle_func_name
                print('ERROR: '+mangle_func_name+' demangle incorrect or unable to demangle')
                data[cnt][file_func_name] = 'ERROR: '+mangle_func_name+' demangle incorrect or unable to demangle'
            else:
                func_name = demangle_func_name.split('(')[0]
                # Try to get code_content, the json file may provide the path or not
                # only get code when pre_file_path!=file_path
                if pre_file_path!=file_path:
                    code_content = get_source_code(file_path, file_name)
                    pre_file_path=file_path
                    print("Open source file: ",pre_file_path)
                    with open('./output/'+proj_name+'/'+json_file_name+'.txt', "w") as fi:
                        # write to JSON file
                        fi.write(code_content)
                if code_content =='ERROR' or code_content=='':
                    print("CODE content ERROR")
                    break
                    continue
                func_content = extract_func_code(func_name,code_content)
                # write to json
                data[cnt][file_func_name] = {'code':func_content,'data': data[cnt][file_func_name]}
    # open the file for writing
    with open('./output/'+proj_name+'/'+json_file_name, "w") as json_file:
        # write to JSON file
        json.dump(data, json_file)