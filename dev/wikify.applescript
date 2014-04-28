--create a global scope list to work with
property g_notes_list : {}
property g_titles_list : {}
property g_links_list : {}
property g_htmls_list : {}

--make sure it's empty as these are persistent between runs
set g_notes_list to {}
set g_titles_list to {}
set g_links_list to {}
set g_htmls_list to {}

--now work with a reference to that global list
set _notes to a reference to g_notes_list
set _titles to a reference to g_titles_list
set _links to a reference to g_links_list
set _htmls to a reference to g_htmls_list


tell application id "com.evernote.Evernote" to set {notes_list, titles_list, links_list, htmls_list} to {every note of notebook "!nbox", title of every note of notebook "!nbox", note link of every note of notebook "!nbox", HTML content of every note of notebook "!nbox"}

set the end of _notes to notes_list
set the end of _titles to titles_list
set the end of _links to links_list
set the end of _htmls to htmls_list

--tell application id "com.evernote.Evernote" to set {notes_list, titles_list, links_list, htmls_list} to {every note of every notebook, title of every note of every notebook, note link of every note of every notebook, HTML content of every note of every notebook}

--set the end of _notes to my ungroup_list(notes_list)
--set the end of _titles to my ungroup_list(titles_list)
--set the end of _links to my ungroup_list(links_list)
--set the end of _htmls to my ungroup_list(htmls_list)

set errors to {}
repeat with i from 1 to (count of (item 1 of _htmls))
	set this_html to (item i of (item 1 of _htmls))
	set this_title to (item i of (item 1 of _titles))
	try
		set clean_html to find text "<body.*?>(.*?)</body>" in this_html using "\\1" regexpflag {"MULTILINE"} with regexp and string result
		repeat with i from 1 to (count of (item 1 of _titles))
			set _title to (item i of (item 1 of _titles))
			if _title is not equal to this_title then
				if not (find text _title in clean_html with whole word, all occurrences and string result) = {} then
					set _url to (item i of (item 1 of _links))
					set _hyperlink to "<a href=\"" & _url & "\">" & _title & "</a>"
					
					set this_html to change _title into _hyperlink in this_html with whole word without case sensitive
					
				end if
			end if
		end repeat
		
		set _note to (item i of (item 1 of _notes))
		
		try
			tell application id "com.evernote.Evernote" to set HTML content of _note to this_html
		on error msg
			return msg
		end try
		
	on error
		copy i to end of errors
	end try
end repeat
errors









(* HANDLERS *)

on ungroup_list(lst)
	local lst, res, itemRef
	try
		if lst's class is not list then error "not a list." number -1704
		script k
			property l : lst
		end script
		if (count k's l each list) is not (count k's l) then ¬
			error "list contains non-list items." number -1704
		set res to {}
		repeat with itemRef in k's l
			set res to res & itemRef's contents
		end repeat
		return res
	on error eMsg number eNum
		error "Can't ungroupList: " & eMsg number eNum
	end try
end ungroup_list

on string_between(str, head, tail)
	local str, head, tail
	try
		if str does not contain head then return ""
		if str does not contain tail then return ""
		set str to item 2 of my explode(head, str)
		set str to item 1 of my explode(tail, str)
		return str
	on error eMsg number eNum
		error "Can't stringBetween: " & eMsg number eNum
	end try
end string_between

on replace(theText, oldString, newString)
	local ASTID, theText, oldString, newString, lst
	set ASTID to AppleScript's text item delimiters
	try
		considering case
			set AppleScript's text item delimiters to oldString
			set lst to every text item of theText
			set AppleScript's text item delimiters to newString
			set theText to lst as string
		end considering
		set AppleScript's text item delimiters to ASTID
		return theText
	on error eMsg number eNum
		set AppleScript's text item delimiters to ASTID
		error "Can't replaceString: " & eMsg number eNum
	end try
end replace

(* SUB-ROUTINES *)

on explode(delimiter, input)
	local delimiter, input, ASTID
	set ASTID to AppleScript's text item delimiters
	try
		set AppleScript's text item delimiters to delimiter
		set input to text items of input
		set AppleScript's text item delimiters to ASTID
		return input --> list
	on error eMsg number eNum
		set AppleScript's text item delimiters to ASTID
		error "Can't explode: " & eMsg number eNum
	end try
end explode