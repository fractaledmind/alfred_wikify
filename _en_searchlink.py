#!/usr/bin/python
# encoding: utf-8
import sys
import os.path
from workflow import Workflow

def main(wf):
	import re
	import codecs
	import applescript as a
	import markdown

	def to_unicode(obj, encoding='utf-8'):
		if isinstance(obj, basestring):
			if not isinstance(obj, unicode):
				obj = unicode(obj, encoding)
		return obj

	if wf.args == 'as':
		# Get input text from temp file
		with codecs.open(wf.cachefile(u"temp.md"), encoding='utf-8') as f:
			txt = f.read()
			f.close()
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
		md_link = a.asrun(script).strip()
		md_link = to_unicode(md_link)
		
		txt = txt.replace(find, md_link)

	mmd = markdown.markdown(txt, extensions=['extra', 'meta'])

	if goal == 'applescript':
		print mmd.encode('utf-8')
	elif goal == 'clipboard':
		script = """
			set the clipboard to {0}
		""".format(a.asquote(mmd))
		a.asrun(script)
		print 'done'
	
if __name__ == '__main__':
	wf = Workflow(libraries=[os.path.join(os.path.dirname(__file__), 'dependencies')])
	sys.exit(wf.run(main)) 
