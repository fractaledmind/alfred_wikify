#!/usr/bin/python
# encoding: utf-8
import re
import sys
import subprocess
from workflow import Workflow
from dependencies import markdown


def uni(obj, encoding='utf-8'):
    """Ensure passed text is Unicode"""
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding)
    return obj

def _as_run(ascript):
    """Run the given AppleScript and return the standard output and error."""
    osa = subprocess.Popen(['osascript', '-'],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE)
    return osa.communicate(ascript)[0]


def main(wf):
    """Primary Function"""
    if wf.args[0] == 'as':
        # Get input text from temp file
        with open(wf.cachefile("temp.md"), 'r') as file_:
            txt = file_.read()
            file_.close()
        goal = 'applescript'
    else:
        txt = wf.args[0]
        goal = 'clipboard'

    en_links = re.findall(r"(\[(.*?)\]\(!en(.*?)\))", txt)

    for link in en_links:
        find = link[0]
        query = link[1]
        args = link[2]
        
        if args == '':
            en_search = '"' + query + '"'
        else:
            en_search = ''
            try: 
                 en_search = en_search + ' notebook:"' + re.search(r"=(.*?)(?=$|\s@)", args).group(1) + '"'
            except AttributeError:
                pass
            try:
                en_search = en_search + ' tag:"' + re.search(r"@(.*?)(?=$|\s=)", args).group(1) + '"'
            except AttributeError:
                pass

        script = """
            tell application "Evernote"
                set _notes to find notes {0}
                repeat with i from 1 to count of _notes
                    set _title to title of (item i of _notes)
                    if _title contains {1} then
                        set _link to note link of (item i of _notes)
                        set md_link to "[" & _title & "](" & _link & ")"
                        return md_link
                    end if
                end repeat
            end tell
        """.format(a.asquote(en_search), a.asquote(query))
        md_link = _as_run(script).strip()
        md_link = uni(md_link)
        
        txt = txt.replace(find, md_link)

    #mmd = markdown.markdown(txt, extensions=['extra', 'meta'])
    mmd = markdown.markdown(txt, ['extra', 'meta'])

    if goal == 'applescript':
        print mmd.encode('utf-8')
    elif goal == 'clipboard':
        script = """
            set the clipboard to {0}
        """.format(a.asquote(mmd))
        _as_run(script)
        print 'done'
    
if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main)) 
