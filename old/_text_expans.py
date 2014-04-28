#!/usr/bin/python
# encoding: utf-8
import sys
import re
import subprocess
from workflow import Workflow

PREFIX = ',,'

def _as_run(ascript):
    """Run the given AppleScript and return the standard output and error."""
    osa = subprocess.Popen(['osascript', '-'],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE)
    return osa.communicate(ascript)[0]

def split_set(item, delim):
    """Define method for splitting multi-line snippet dictionaries"""
    if delim in item:
        split = filter(None, item.split(delim))
        return split


def main(wf):
    """Primary Function"""
    
    if wf.args[0] == 'as':
        # Get input text from temp file
        with open(wf.cachefile("temp.md"), 'r') as file_:
            the_str = file_.read()
            file_.close()
        goal = 'applescript'
    else:
        the_str = wf.args[0]
        goal = 'clipboard'
    
    # Find all snippet dictionaries
    _snippets = re.findall(r"\^{3}(.*?)\^{3}", the_str, re.S)

    # Create Python snippet dictionary
    _dict = {}
    for i in _snippets:
        # If multi-line with ``carriage return``
        if '\r' in i:
            sub_l = split_set(i, '\r')
            for sub in sub_l:
                try:
                    [key, val] = sub.split(':')
                    _dict[key.strip()] = val.lstrip()
                except:
                    pass
        
        # If multi-line with ``newline``
        elif '\n' in i:
            sub_l = split_set(i, '\n')
            for sub in sub_l:
                try:
                    [key, val] = sub.split(':')
                    _dict[key.strip()] = val.lstrip()
                except:
                    pass
        
        # If single line
        else:
            [key, val] = i.split(':')
            _dict[key.strip()] = val.lstrip()

    # Find and replace all snippets with expanded text
    for key in sorted(_dict, key=len, reverse=True):
        new_key = PREFIX + key
        the_str = the_str.replace(new_key, _dict[key])
    
    # Remove all snippet dictionaries from text
    the_str = re.sub(r"\^{3}(.*?)\^{3}", "", the_str)

    # Return the expanded, clean text
    if goal == 'applescript':
        print the_str.encode("utf-8")
    elif goal == 'clipboard':
        script = """
            set the clipboard to "{0}"
        """.format(the_str)
        _as_run(script)
        print 'done'
        
if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
