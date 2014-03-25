#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import json
import applescript as a
import markdown



txt = """
**Examples**

* General Query: [PDF Management](!en)
* Notebook-Limited Query: [CAMWS registration](!en =!nbox)
* Tag-Limited Query: [Apollonius](!en @wiki)
* Notebook- and Tag-Limited Query: [Tools](!en =postach.io @page)
"""

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
	md_link = a.asrun(script).strip()
	
	txt = txt.replace(find, md_link)

print markdown.markdown(txt, extensions=['extra', 'meta'])


