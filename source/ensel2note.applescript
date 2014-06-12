on run argv
	
	(* ///
	PRELIMINARIES 
	/// *)
	
	--get input
	if (argv as string) = "" then
		set md_source to the clipboard
	else
		set md_source to (argv as string)
	end if
	
	
	tell application id "com.evernote.Evernote"
		set en_sel to selection
		if en_sel is {} then display dialog "Please select a note."
		
		repeat with i from 1 to (count of en_sel)
			
			(* ///
			PART ONE: Create New Note
			/// *)
			
			--get appropriate note data from current note
			set note_url to note link of (item i of en_sel)
			set note_name to title of (item i of en_sel)
			set note_nb to name of notebook of (item i of en_sel)
			set note_html to HTML content of (item i of en_sel)
			
			--generate the hyperlink
			set org_html_ref to "<a href=\"" & note_url & "\">" & note_name & "</a>"
			
			--create the new note, with the hyperlink back
			set new_note to create note title md_source with html org_html_ref notebook note_nb
			
			--synchronize to assign server data to new note
			my en_sync()
			
			(* ///
			PART TWO: Link to New Note
			/// *)
			
			--get appropriate data of the new note
			set new_url to note link of new_note
			set new_name to title of new_note
			set new_html_ref to "<a href=\"" & new_url & "\">" & new_name & "</a>"
			
			--replace the selected text with a hyperlink
			set new_html to my replace_string(note_html, md_source, new_html_ref)
			set HTML content of (item i of en_sel) to new_html
			
			--synchronize again to finalize everything
			my en_sync()
		end repeat
	end tell
end run


(* HANDLERS *)

on replace_string(full_string, find_string, replace_string)
	-- ljr (http://applescript.bratis-lover.net/library/string/)
	local ASTID, full_string, find_string, replace_string, lst
	set ASTID to AppleScript's text item delimiters
	try
		considering case
			set AppleScript's text item delimiters to find_string
			set lst to every text item of full_string
			set AppleScript's text item delimiters to replace_string
			set full_string to lst as string
		end considering
		set AppleScript's text item delimiters to ASTID
		return full_string
	on error eMsg number eNum
		set AppleScript's text item delimiters to ASTID
		error "Can't replace_string: " & eMsg number eNum
	end try
end replace_string

on en_sync()
	tell application id "com.evernote.Evernote"
		repeat until isSynchronizing is false
		end repeat
		synchronize
		repeat until isSynchronizing is false
		end repeat
	end tell
end en_sync