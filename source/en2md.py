#!/usr/bin/python
# encoding: utf-8
import sys
import subprocess
from workflow import Workflow

from dependencies import html2text

GET_EN_DATA = """
    tell application id "com.evernote.Evernote"
        set _sel to selection
        if _sel is {} then error "Please select a note."
        
        repeat with i from 1 to the count of _sel
            --get note title and notebook name
            set _title to title of item i of _sel
            set _notebook to name of notebook of item i of _sel
            
            --get list of tags into comma-separated string
            set _tags to tags of item i of _sel
            set tags_lst to {}
            repeat with j from 1 to count of _tags
                copy (name of item j of _tags) to the end of tags_lst
            end repeat
            set _tags to my join_list(tags_lst, ", ")
            
            --get note HTML
            set note_html to HTML content of item i of _sel
        end repeat
    end tell

    set {tid, AppleScript's text item delimiters} to {AppleScript's text item delimiters, return & "||" & return}
    set l to {_title, _notebook, _tags, note_html} as string
    set AppleScript's text item delimiters to tid
    return l

    to join_list(aList, delimiter)
        set retVal to ""
        set prevDelimiter to AppleScript's text item delimiters
        set AppleScript's text item delimiters to delimiter
        set retVal to aList as string
        set AppleScript's text item delimiters to prevDelimiter
        return retVal
    end join_list
"""

def _unify(obj, encoding='utf-8'):
    """Ensure passed text is Unicode"""
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding)
    return obj

##################################################
### AppleScript Functions
##################################################

def as_run(ascript):
    """Run the given AppleScript and return the standard output and error."""
    ascript = _unify(ascript)
    osa = subprocess.Popen(['osascript', '-'],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE)
    return osa.communicate(ascript.encode('utf-8'))[0].strip()


def main(wf):
    """Convert Evernote note to Markdown file"""

    # Get all relevant data from selected Evernote note as Unicode text
    en_data = _unify(as_run(GET_EN_DATA))

    # Extract Evernote note data
    (en_title, en_notebook, en_tags, en_html) = en_data.split('\r||\r')

    # Convert Evernote note HTML to Markdown
    en_md = html2text.html2text(en_html)

    # Prepare MMD metadata headers
    en_meta = ['# ' + en_title + '  ',
               '= ' + en_notebook + '  ']
    if en_tags != "":
        en_meta += ['@ ' + en_tags + '  ']

    # Prepare MMD text
    en_meta += ['\n', en_md]

    # Convert list to full text
    en_md = '\n'.join(en_meta)
    
    # Prepare path to cached file
    md_file = wf.cachefile(en_title + '.md')

    # Write MD text to cached file
    with open(md_file, 'w') as file_obj:
        file_obj.write(en_md)
        file_obj.close()

    # Open new MD file
    subprocess.call(['open', md_file])

  
if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
