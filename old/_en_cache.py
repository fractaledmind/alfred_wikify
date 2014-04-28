#!/usr/bin/python
# encoding: utf-8
import subprocess
import json

def _as_run(ascript):
    """Run the given AppleScript and return the standard output and error."""
    osa = subprocess.Popen(['osascript', '-'],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE)
    return osa.communicate(ascript)[0]

def get_en_data(data_type):
    """Use Applescript to get list of Evernote data"""
    scpt = """
        set {{astid, AppleScript's text item delimiters}} to {{AppleScript's text item delimiters, "||"}}
        tell application id "com.evernote.Evernote" to set n_data to {0} of every note of every notebook as string
        set AppleScript's text item delimiters to astid
        return n_data
    """.format(data_type)
    _res = _as_run(scpt).strip()
    _lst = _res.split("||")
    return _lst


def main():
    """Create Evernote cache"""
    
    titles_lst = get_en_data('title')
    links_lst = get_en_data('note link')

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
    
    # pretty print dictionary as JSON
    final_json = json.dumps(final_dict, 
                            sort_keys=False, 
                            indent=4, 
                            separators=(',', ': '))
    with open('/Users/smargheim/Desktop/en_cache.json', 'w') as file_:
        file_.write(final_json.encode('utf-8'))
        file_.close()


if __name__ == '__main__':
    main()
