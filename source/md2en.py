#!/usr/bin/python
# encoding: utf-8
from __future__ import unicode_literals

import re
import sys
import time
import urllib
import os.path
import subprocess
from workflow import Workflow
from dependencies import markdown

PREFIX = ',,'
PDF_DIR = '/Users/smargheim/Documents/PDFs' #!!CHANGE TO YOUR PDF DIRECTORY!!

CREATE_NOTE = """
    tell application id "com.evernote.Evernote"
        --ensure notebook exists
        if (not (notebook named "{nb}" exists)) then
            make notebook with properties {{name:"{nb}"}}
        end if
        
        --create the note
        set the_note to create note title "{title}" with html "{html}" notebook "{nb}"
        
        --assign tags
        set tag_list to {tags}
        repeat with i from 1 to count of tag_list
            set _tag to item i of tag_list
            if (not (tag named _tag exists)) then
                set en_tag to make tag with properties {{name:_tag}}
            else
                set en_tag to tag _tag
            end if
            assign en_tag to the_note
        end repeat
    end tell
    return "Created " & "{title}" & " in " & "{nb}"
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

def _applescriptify_str(text):
    """Replace double quotes in text for Applescript string"""
    text = _unify(text)
    return text.replace('"', '" & quote & "')

def _applescriptify_list(_list):
    """Convert Python list to Applescript list"""
    quoted_list = []
    for item in _list:
        if type(item) is unicode:   # unicode string to AS string
            _new = '"' + item + '"'
            quoted_list.append(_new)    
        elif type(item) is str:     # string to AS string
            _new = '"' + item + '"'
            quoted_list.append(_new)    
        elif type(item) is int:     # int to AS number
            _new = str(item)
            quoted_list.append(_new)
        elif type(item) is bool:    # bool to AS Boolean
            _new = str(item).lower()
            quoted_list.append(_new)
    quoted_str = ', '.join(quoted_list)
    return '{' + quoted_str + '}'

def as_run(ascript):
    """Run the given AppleScript and return the standard output and error."""
    ascript = _unify(ascript)
    osa = subprocess.Popen(['osascript', '-'],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE)
    return osa.communicate(ascript.encode('utf-8'))[0].strip()

def get_clipboard(): 
    """Get objects of clipboard"""
    return as_run("return the clipboard").strip()


##################################################
### Extract Metadata Function
##################################################

def get_metadata(_str, _origin):
    """Extract and remove all note metadata"""
    if _origin == 'clipboard':
        _delim = '\r'
    elif _origin == 'args':
        _delim = '\n'

    if _str.startswith('Title: ') or _str.startswith('# '):
        title_meta = _str.split(_delim, 1)[0]
        en_title = title_meta.split(' ', 1)[1].strip()
        _str = _str.replace(title_meta + _delim, '')
    else:
        en_title = time.strftime("%d-%m-%Y")

    if _str.startswith('Notebook: ') or _str.startswith('= '):
        nb_meta = _str.split(_delim, 1)[0]
        en_nb = nb_meta.split(' ', 1)[1].strip()
        _str = _str.replace(nb_meta + _delim, '')
    else:
        en_nb = as_run("""tell application id "com.evernote.Evernote" to """ \
                        """return name of notebook 1 whose default is true""")

    if _str.startswith('Tags: ') or _str.startswith('@ '):
        tag_meta = _str.split(_delim, 1)[0]
        en_tags = tag_meta.split(' ', 1)[1].strip()
        en_tags = en_tags.split(', ')
        _str = _str.replace(tag_meta + _delim, '')
    else:
        en_tags = ['wiki']

    return {
        'title': en_title, 
        'notebook': en_nb,
        'tags': en_tags,
        'text': _str
    }


##################################################
### Expand In-Text Snippets Functions
##################################################

def _split_set(item, delim):
    """Split multi-line snippet dictionaries"""
    if delim in item:
        split = filter(None, item.split(delim))
        return split
    else:
        return item

def _snippet_dict(item, delim):
    """Create Python snippet dictionary"""
    _dict = {}
    if delim in item:
        sub_l = _split_set(item, delim)
        for sub in sub_l:
            [key, val] = sub.split(':')
            _dict[key.strip()] = val.lstrip()
    return _dict

def expand_snippets(the_str):
    """Find, Expand, and Replace any in-text snippets"""
    _snippets = re.findall(r"\^{3}(.*?)\^{3}", the_str, flags=re.S)

    _dict = {}
    for i in _snippets:
        if '\r' in i: 
            # If multi-line with ``carriage return``
            _dict.update(_snippet_dict(i, '\r'))
        elif '\n' in i:
            # If multi-line with ``newline``
            _dict.update(_snippet_dict(i, '\n'))
        else:
            # If single line
            [key, val] = i.split(':')
            _dict[key.strip()] = val.lstrip()

    # Find and replace all snippets with expanded text
    for key in sorted(_dict, key=len, reverse=True):
        new_key = PREFIX + key
        the_str = the_str.replace(new_key, _dict[key])
    
    # Remove all snippet dictionaries from text
    the_str = re.sub(r"\^{3}(.*?)\^{3}", "", the_str, flags=re.S)
    return the_str


##################################################
### Wikify Pre-Existing Notes Functions
##################################################

def _get_en_data(data_type):
    """Use Applescript to get list of Evernote data"""
    scpt = """
        set {{astid, AppleScript's text item delimiters}} to {{AppleScript's text item delimiters, "x||x"}}
        tell application id "com.evernote.Evernote" to set n_data to {0} of every note of every notebook as string
        set AppleScript's text item delimiters to astid
        return n_data
    """.format(_applescriptify_str(data_type))
    _res = as_run(scpt).strip()
    _lst = _unify(_res).split("x||x")
    return _lst

def _en_cache():
    """Get cache of all Evernote titles and note links"""
    titles_lst = _get_en_data('title')
    links_lst = _get_en_data('note link')

    # interlace lists
    final_lst = [val for pair in zip(titles_lst, links_lst) for val in pair]
    # group flat list into pairs
    group_lst = zip(*[iter(final_lst)] * 2)

    # create dictionary from paired items
    final_dict = []
    for pair in group_lst:
        if pair[0] != "":
            _dct = {'title': pair[0], 'link': pair[1]}
            final_dict.append(_dct)
    return final_dict

def wikify_old(_str):
    """Find and replace all occurences of EN titles"""
    en_notes = _en_cache()

    for _nt in en_notes:
        if _nt['title'] in _str:
            md_ref = '[' + _nt['title'] + '](' + _nt['link'] + ')'
            _str = _str.replace(_nt['title'], md_ref)
    return _str


##################################################
### Wikify PDFs Functions
##################################################

def wikify_pdfs(_str):
    """Automatically hyperlink to PDFs in Zotero directory"""

    skimmer_url = "skimmer://{path}?page=0"

    if os.path.exists(PDF_DIR):
        pdf_query = """mdfind "(kMDItemKind == 'PDF')" \
            -onlyin '{dir}'""".format(
                dir=PDF_DIR)
        pdf_str = subprocess.check_output(pdf_query, shell=True)
        pdf_uni = _unify(pdf_str)
        pdf_list = pdf_uni.split("\n")
        if pdf_list[-1] == "":
            pdf_list = pdf_list[:-1]

        for pdf in pdf_list:
            pdf_title = pdf.split("/")[-1]
            clean_title = pdf_title.replace('.pdf', '')
            if clean_title in _str:
                html_path = urllib.quote(pdf)
                _url = skimmer_url.format(
                    path=html_path)
                md_ref = '[' + pdf_title + '](' + _url + ')'
                _str = _str.replace(clean_title, md_ref)
    return _str


##################################################
### Wikify New Notes Functions
##################################################

def _new_wikis(_list, _nb, _note):
    """Create new notes"""
    as_list = _unify(_applescriptify_list(_list))

    scpt = """
    set _links to {{}}
    tell application id "com.evernote.Evernote"
        set _continue to false
        set _list to {0}
        set _nb to "{1}"
        repeat with i from 1 to count of _list
            set _word to (item i of _list)
            set matches to find notes "intitle:\\"" & _word & "\\" notebook:\\"{1}\\""
            
            if matches = {{}} then
                set _note to create note title _word with text "" notebook "{1}"
                if (not (tag named "wiki" exists)) then
                    make tag with properties {{name:"wiki"}}
                end if
                set _tag to tag "wiki"
                assign _tag to _note
                if (not (tag named "{2}" exists)) then
                    make tag with properties {{name:"{2}"}}
                end if
                set _tag to tag "{2}"
                assign _tag to _note
                set _continue to true
            end if
        end repeat
        if _continue = true then
            repeat until isSynchronizing is false
            end repeat
            synchronize
            repeat until isSynchronizing is false
            end repeat
        end if
        set new_notes to find notes "tag:wiki tag:\\"{2}\\" notebook:\\"{1}\\""
        delay 0.3
        repeat with i from 1 to count of new_notes
            set _url to (note link of (item i of new_notes))
            set _title to (title of (item i of new_notes))
            set _md to "[" & _title & "](" & _url & ")"
            copy _md to end of _links
        end repeat
        set {{astid, AppleScript's text item delimiters}} to {{AppleScript's text item delimiters, "x||x"}}
        set _list to _links as string
        set AppleScript's text item delimiters to astid
        return _list
    end tell
    """.format(as_list, _nb, _note)
    _res = as_run(scpt)
    return _unify(_res).split('x||x')

def wikify_new(_txt, meta_data):
    """Create and link to new notes"""
    wiki_list = re.findall(r"\[\[(.*?)\]\]", _txt)
    if len(wiki_list) > 0:
        md_links = _new_wikis(wiki_list, 
                              meta_data['notebook'], 
                              meta_data['title'])

        if len(wiki_list) == len(md_links):
            for i, lnk in enumerate(md_links):
                find = '[[' + wiki_list[i] + ']]'
                _txt = _txt.replace(find, lnk)
        else:
            print "Length error! {}".format(md_links)
    return _txt


##################################################
### Get Input Text
##################################################

def get_input(wf):
    """Get text input from Alfred"""
    if wf.args[0] == '':
        # Get input text from clipboard
        the_str = get_clipboard()
        _origin = 'clipboard'
    else:
        the_str = wf.args[0]
        _origin = 'args'
    return {'str': _unify(the_str), 'source': _origin}


##################################################
### Wikify Main
##################################################

def main(wf):
    """Primary Function"""
    
    # Get input text
    _str = get_input(wf)
    #_str = get_clipboard()
    _str = _unify(_str)
    
    # Process and extract metadata
    str_dict = get_metadata(_str['str'], _str['source'])
    #str_dict = get_metadata(_str, 'clipboard')
    #print "METADATA\n"      #VERBOSE
    #print str_dict         #VERBOSE
    #print '- - -\n\n'      #VERBOSE

    # Expand any in-text snippets
    new_str = expand_snippets(str_dict['text'])
    #print "SNIPPETS\n"      #VERBOSE
    #print new_str.encode('utf-8')          #VERBOSE
    #print '- - -\n\n'      #VERBOSE

    # Wiki-link to any matched pre-existing EN notes
    linked_str = wikify_old(new_str)
    #print "OLD-LINKS\n"      #VERBOSE
    #print linked_str.encode('utf-8')      #VERBOSE
    #print '- - -\n\n'      #VERBOSE

    # Wiki-link to any matched PDFs in specified dir
    pdf_str = wikify_pdfs(linked_str)
    #print "PDF-LINKS\n"      #VERBOSE
    #print pdf_str.encode('utf-8')         #VERBOSE
    #print '- - -\n\n'      #VERBOSE

    # Wiki-link to any marked new EN notes
    wiki_str = wikify_new(pdf_str, str_dict)
    #print "NEW-LINKS\n"      #VERBOSE
    #print wiki_str.encode('utf-8')         #VERBOSE
    #print '- - -\n\n'      #VERBOSE

    # Convert MD to HTML
    html_str = markdown.markdown(wiki_str)
    
    # Create new HTML Evernote note
    create_scpt = CREATE_NOTE.format(
            nb=_applescriptify_str(str_dict['notebook']),
            title=_applescriptify_str(str_dict['title']),
            html=_applescriptify_str(html_str),
            tags=_applescriptify_list(str_dict['tags'])
        )
    print as_run(create_scpt)

        
if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
