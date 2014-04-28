#!/usr/bin/python
# encoding: utf-8
import json
import subprocess

def _as_run(ascript):
    """Run the given AppleScript and return the standard output and error."""
    osa = subprocess.Popen(['osascript', '-'],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE)
    return osa.communicate(ascript)[0]

def get_clipboard(): 
    """Get objects of clipboard"""
    return _as_run("return the clipboard").strip()


def main():
    """Primary function"""

    #if wf.args[0] == 'as':
    #    # Get input text from temp file
    #    with open(wf.cachefile("temp.md"), 'r') as file_:
    #        the_str = file_.read()
    #        file_.close()
    #    goal = 'applescript'
    #else:
    #    the_str = wf.args[0]
    #    goal = 'clipboard'

    _txt = get_clipboard()

    with open('/Users/smargheim/Desktop/en_cache.json', 'r') as file_:
        en_notes = json.load(file_)
        file_.close()

    _new = _txt
    for n in en_notes:
        if n['title'].lower() in _txt.lower():
            html_ref = '<a href="' + n['link'] + '">' + n['title'] + '</a>'
            _new = _new.replace(n['title'], html_ref)


    print _txt
    print '- - -'
    print _new


if __name__ == '__main__':
    main()
