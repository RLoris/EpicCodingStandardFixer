import glob, os, re

'''
Called to fix the above comment about copyright
'''
def fix_copyright_comment(file: str, source_code: str, new_copyright: str):
    # skip if already there or thirdparty sources
    if(source_code.find(new_copyright) != -1 or file.find("ThirdParty") != -1):
        return source_code
    # check BOM 'UTF-8' start
    start_idx = 0
    if(len(source_code) >= 3 and source_code[0] == 0xEF and source_code[1] == 0xBB and source_code[2] == 0xBF):
        start_idx+=3
    # find first character like include or class
    skip_chars = 0
    for c in source_code[start_idx:]:
        skip_chars+=1
        if c == "#" or re.match("\w", c):
            break
    # remove old copyright comment
    match = re.match("//.*copyright.*", source_code, re.M | re.I)
    if (match):
        source_code = source_code[:match.span()[0]] + source_code[match.span()[1]:]
    # insert new comment
    print(f"/!\ Fix copyright needed in file: {file}\n")
    print(f"BEFORE\n+++\n{source_code[:len(new_copyright)]}---")
    source_code = source_code[:start_idx] + new_copyright + source_code[start_idx:]
    print(f"AFTER\n+++\n{source_code[:len(new_copyright)]}---")
    return source_code

'''
Called to fix block brackets with epic standard code guideline
'''
def fix_if_block(file:str, source_code: str):
    start_idx = 0
    end_idx = len(source_code) - 1
    trigger_word = "if"
    while True:
        if_idx = source_code.find(trigger_word, start_idx, end_idx)
        if (if_idx == -1):
            break
        # skip if not special space character before, macros, preprocessor instructions will be skipped here
        if not (re.match("\s", source_code[if_idx-1])):
            break
        # skip trigger word to avoid looping
        start_idx = if_idx + len(trigger_word)
        # go to last condition closing bracket
        bracket_depth = 0
        skip_chars = 0
        jump_line = False
        # find end of condition
        for c in source_code[start_idx:]:
            skip_chars+=1
            if jump_line and re.match("\n", c):
                jump_line = False
                continue
            elif (c == "("): 
                bracket_depth+=1
            elif (c == ")"):
                bracket_depth-=1
                # closing if condition
                if (bracket_depth == 0):
                    break
            # probably an comment
            elif (bracket_depth == 0 and (not re.match("\s", c))):
                jump_line = True
                break
        # find whether we need to fix block
        end_condition = start_idx+skip_chars
        fix_if = False
        skip_chars = 0
        jump_line = False
        for c in source_code[end_condition:]:
            skip_chars+=1
            if (jump_line and re.match("\n", c)):
                jump_line = False
                continue
            if not jump_line and not (re.match("\s", c)):
                # inline comment //
                if (c == "/"):
                    jump_line = True
                    continue
                # next instruction
                if not (c == "{"):
                    fix_if = True
                break
        start_block = end_condition+skip_chars
        # no need fixing skip
        if not (fix_if):
            continue
        # find end of block
        skip_chars = 0
        for c in source_code[start_block:]:
            skip_chars+=1
            if(re.match(";", c)):
                break
        end_block = start_block + skip_chars
        # find block indent
        indent = ''
        skip_chars = 0
        while True:
            skip_chars+=1
            if (re.match("(\r\n|\r|\n)", source_code[if_idx-skip_chars])):
                break
            elif (re.match("\s", source_code[if_idx-skip_chars])):
                indent = source_code[if_idx-skip_chars] + indent
        # perform fix
        if fix_if:
            # avoid adding newline if already exists
            new_line_idx = source_code[end_condition:start_block].find('\n')
            # remove original indent
            skip_chars = 0
            if (new_line_idx != -1):
                for c in source_code[end_condition+new_line_idx+1:]:
                    if re.match("\s", c):
                        skip_chars+=1
                    else:
                        break
            print(f"/!\ Fix if needed in file: {file}\n")
            print(f"BEFORE\n+++\n{source_code[start_idx-2:end_block+2]}---")
            fixed_block = ('' if (new_line_idx != -1) else f"\n") + indent + "{\n\t" + indent + source_code[start_block-1:end_block] + "\n" + indent + "}" 
            source_code = source_code[:start_block-1-skip_chars] + fixed_block + source_code[end_block:]
            print(f"AFTER\n+++\n{source_code[start_idx-2:end_block+4]}---")
    return source_code

'''
Prompts the user for the input source folder to scan
'''
def prompt_source_folder():
    source_folder = ""
    while True:
        source_folder = input("Insert source path folder to search recusively: ")
        if os.path.exists(source_folder):
            break
    return source_folder

'''
Prompts the user to input new copyright comment to replace old one or leave empty for no replacement
'''
def prompt_copyright_comment():
    new_copyright = ""
    while True:
        new_copyright = input("Insert new copyright comment for source files (without '// Copyright') or leave empty: ")
        # avoid new lines or carriage returns
        if not (re.match("(\r\n|\r|\n)", new_copyright)):
            break
    if (len(new_copyright) > 0):
        new_copyright = "// Copyright " + new_copyright + "\n"
        print(f"New copyright comment will be: {new_copyright}")
    else:
        new_copyright = ""
        print("Copyright comment will not be updated")
    return new_copyright

'''
Scan recursively source folder for cpp/h files and returns the path list
'''
def scan_source_folder(source_folder: str):
    # scan for .cpp & .h file only
    source_files = []
    for ext in (".h", ".cpp"):
        source_files.extend(glob.glob(f"{source_folder}/**/*{ext}", recursive=True))
    total_files = len(source_files)
    print(f"Total files found (*.h|*.cpp): {total_files}")
    confirm = input("Continue with the update process [Y-N]: ")
    if (confirm != "Y"):
        exit()
    return source_files

'''
Update the files in source list with various fixes and write them to disk
'''
def update_source_files(source_files: list, new_copyright: str):
    total_updates = 0
    # recurse through source directory
    for file in source_files:
        with open(file, "r+") as f:
            source_code = f.read()
            updated_code = source_code
            # only .cpp files
            if (file.endswith(".cpp")):
                updated_code = fix_if_block(file, source_code)
            # header + cpp files
            if (len(new_copyright) != 0):
                updated_code = fix_copyright_comment(file, updated_code, new_copyright)
            # change detected
            if (source_code != updated_code):
                total_updates+=1
                # replace content
                f.seek(0)
                f.write(updated_code)
                f.truncate()
    return total_updates

'''
Main entry
'''
if __name__ == "__main__":
    source_folder = prompt_source_folder()
    new_copyright = prompt_copyright_comment()
    source_files = scan_source_folder(source_folder)
    total_updates = update_source_files(source_files, new_copyright)
    print(f"Total files updated: {total_updates}")
    if (total_updates > 0):
        print(f"Check updated files before commiting and pushing to source control")
