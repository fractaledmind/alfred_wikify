#!/usr/bin/python
# encoding: utf-8
import sys
import os.path
from workflow import Workflow

def main(wf):
	import applescript as a
	import re
	import codecs

	if wf.args == 'as':
		# Get input text from temp file
		with codecs.open(wf.cachefile(u"temp.md"), encoding='utf-8') as f:
			the_str = f.read()
			f.close()
		goal = 'applescript'
	else:
		the_str = wf.args[0]
		goal = 'clipboard'
	
	# Find all snippet dictionaries
	l = re.findall(r"\^{3}(.*?)\^{3}", the_str, re.S)

	# Define method for splitting multi-line snippet dictionaries
	def split_set(item, delim):
		if delim in item:
			return filter(None, item.split(delim))

	# Create Python snippet dictionary
	d = {}
	for i in l:
		# If multi-line with ``carriage return``
		if '\r' in i:
			sub_l = split_set(i, u'\r')
			for s in sub_l:
				try:
					[k, v] = s.split(':')
					d[k.strip()] = v.lstrip()
				except:
					pass
		
		# If multi-line with ``newline``
		elif '\n' in i:
			sub_l = split_set(i, u'\n')
			for s in sub_l:
				try:
					[k, v] = s.split(u':')
					d[k.strip()] = v.lstrip()
				except:
					pass
		
		# If single line
		else:
			[k, v] = i.split(u':')
			d[k.strip()] = v.lstrip()

	# Find and replace all snippets with expanded text
	for k in sorted(d, key=len, reverse=True):
		nk = ',,' + k
		the_str = the_str.replace(nk, d[k])
	
	# Remove all snippet dictionaries from text
	the_str = re.sub(r"\^{3}(.*?)\^{3}", "", the_str)

	# Return the expanded, clean text
	if goal == 'applescript':
		print the_str.encode("utf-8")
	elif goal == 'clipboard':
		script = """
			set the clipboard to {0}
		""".format(a.asquote(the_str))
		a.asrun(script)
		print 'done'
		
if __name__ == '__main__':
	wf = Workflow(libraries=[os.path.join(os.path.dirname(__file__), 'dependencies')])
	sys.exit(wf.run(main))
