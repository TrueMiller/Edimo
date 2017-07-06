import re
import subprocess
import sys

def get_command(fildes):
#TODO: This..
    if not isinstance(fildes, file):
        return input("__Command__\n")
    else:
        return fildes.read()

def split_command(cmd_str):
    command = _extract_cmd(cmd_str)
    options = _get_options(command)
    options = _remove_options(options)
    matches = _match_keywords(cmd_str, options)
    ordered_matches = _order_matches(matches)
    output = [cmd_str[0:ordered_matches[0][0]-1] + " \\\n"]
    for i in range(0, len(ordered_matches)-1):
        output.append(_format_command_parameter(cmd_str, ordered_matches[i][0], ordered_matches[i+1][0])) 
    i += 1
    output.append(_format_command_parameter(cmd_str, ordered_matches[i][0])) 
    return "".join(output).rstrip()

def parse_man_file(man_page):
    options = False
    keywords = set()
    with open(man_page, "r") as f:
        for line in f.readlines():
            if not options:
                options = _set_flag(line)
                continue
            else:
                if _remove_flag(line):
                    break
            if options:
                param_config = _get_keyword(line)
                if param_config["short"] is not None:
                    keywords.add((param_config["short"], param_config["user-value"]))
                if param_config["long"] is not None:
                    keywords.add((param_config["long"], param_config["user-value"]))
    return keywords

def _attr_style(line, idx):
    if line[idx] == '-':
        if line[idx+1] == '-':
           return "long"
        else:
           return "short"
    else:
        return "user-value"

def _extract_cmd(cmd_str):
    buffer_ = ""
    for c in cmd_str.lstrip():
        if c.isspace():
            return buffer_
        buffer_ += c
    #If cmd_str is just COMMAND
    return cmd_str

def _format_command_parameter(line, start_idx, end_idx=None):
   if end_idx is not None:
       return line[start_idx:end_idx] + "\\\n" 
   else:
       return line[start_idx:]
 
def _get_kw(line, delims, param_config):
    line = line.lstrip()
    if not line:
        return param_config, line
    idx = _attr_style(line, 0)
    buffer_ = ""
    for i in range(0, len(line)):
        if line[i] in delims:
            #Need to move past delimiter for next call.
            i += 1
            break
        buffer_ += line[i]
    param_config[idx] = buffer_.rstrip()
    line = line[i:]
    return param_config, line

def _get_keyword(line, delims=[",", " ", "="]):
    param_config = {"short": None, "long": None, "user-value": None}
    if line[0:8] == ".IX Item":
        line = line.replace("\"", " ")[9:]
    elif line[0:3] == ".IP":
        line = line.replace("\"", " ")[3:]
    else:
        return param_config
    while line != "":
        param_config, line = _get_kw(line, delims, param_config)
    return param_config

def _get_man_page_location(cmd):
    return subprocess.check_output(["/bin/sh", "-c", "man -w " + cmd], universal_newlines=True)
    
def _get_options(cmd):
    fileLocations = _get_man_page_location(cmd)
    for f in fileLocations.split("\n"):
        return parse_man_file(f)
    return None
        
def _match_keywords(cmd_str, options):
    results = {}
    for keyword, value in options:
        for i in range(0, len(cmd_str)-len(keyword)):
            if keyword == cmd_str[i:i+len(keyword)] and cmd_str[i-1].isspace():
                if keyword not in results:
                    results[keyword] = {"idx_matches":[i], "user-value": value}
                else:
                    results[keyword]["idx_matches"].append(i)
    return results

def _order_matches(matches):
    ordered_matches = []
    for param in matches:
        for idx in matches[param]["idx_matches"]:
            flg_insert = False
            if ordered_matches:
                for i in range(0, len(ordered_matches)):
                    if ordered_matches[i][0] > idx:
                        ordered_matches.insert(i, (idx, param))
                        flg_insert = True
                        break
            if not flg_insert:
                #Case A: first to be inserted
                #Case B: idx is greater than all ordered matches
                ordered_matches.append((idx, param))
    return ordered_matches

def _output(matches, ignore_first_matches):
    output = []
    for match in matches:
        if ignore_first_matches > 0:
            ignore_first_matches -= 1
            output.append(match)
        else:
            output.append(match)
            output.append(format_new_line())
    return "".join(output)

def _remove_flag(line, pattern="^.SH \w{1}"):
    if re.match(pattern, line) is not None:
        return True
    else:
        return False

def _remove_options(options, default="-,--"):
    #Should use dictionary instead of set.
    #Since the user-value could be none or something, we have 
    #to obtain the entire value so that we can call remove obj
    #from the set. 
    #We must wait till we are done using the set to remove obj.

    opts_to_rm = default.split(",")
    pending_removal = []
    for op in options:
        if op[0] in opts_to_rm:
            pending_removal.append(op)
    for op in pending_removal:
        options.remove(op)
    return options
              
def _set_flag(line, pattern="^.SH (\")?OPTIONS"):
    if re.match(pattern, line) is not None:
        return True
    else:
        return False
   
if __name__ == "__main__":
    cmd_str = get_command(sys.stdin)
    print (split_command(cmd_str))
