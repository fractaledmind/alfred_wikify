on run
	
	tell application id "com.evernote.Evernote"
		--get Evernote selection (multiple allowed)
		set _sel to selection
		if _sel = {} then return "Please select a note"
		
		--get lists of all note titles and urls
		set titles_list to title of every note of every notebook
		set links_list to note link of every note of every notebook
		set _titles to my ungroup_list(titles_list)
		set _links to my ungroup_list(links_list)
		
		
		repeat with i from 1 to count of _sel
			set this_html to HTML content of (item i of _sel)
			set html_copy to this_html
			--extract HTML body text
			set html_body to find text "<body.*?>(.*?)</body>" in this_html using "\\1" regexpflag {"MULTILINE"} with regexp and string result
			
			repeat with x from 1 to (count _titles)
				set _title to (item x of _titles)
				--check if HTML contains the note title
				if this_html contains _title then
					set _url to (item x of _links)
					set _hyperlink to "<a href=\"" & _url & "\">" & _title & "</a>"
					set html_copy to change _title into _hyperlink in html_copy with whole word without case sensitive
				end if
			end repeat
			
			--replace note's HTML content with hyperlinked version
			set HTML content of (item i of _sel) to html_copy
		end repeat
	end tell
end run

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