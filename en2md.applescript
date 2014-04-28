property LF : (ASCII character 32) & (ASCII character 32) & (ASCII character 10)

on run
	
	(* ///
	PRELIMINARIES 
	/// *)
	
	--get path to current directory
	set base_path to my get_base_path()
	
	--prepare path to Python converter script
	set html_processor to base_path & "dependencies/html2text.py"
	
	--load helper script
	set wf to load script ((base_path & "dependencies/_wf-helpers.scpt"))
	
	--ensure storage and cache directories exist
	wf's init_paths()
	
	--prepare key paths
	set storage_path to wf's get_storage()
	set cache_path to wf's get_cache()
	
	(* ///
	PART ONE: Get HTML and relevant data from Selected Evernote note 
	/// *)
	
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
	
	--remove unnecessary xml header
	set raw_html to my remove_from_string(note_html, "<?xml version=\"1.0\" encoding=\"UTF-8\"?><!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\"><html xmlns=\"http://www.w3.org/1999/xhtml\">")
	
	--write HTML to temp file
	set html_target to (cache_path & _title & ".html")
	my write_to_file(raw_html, html_target, false)
	
	(* ///
	PART TWO: Convert HTML to Markdown
	/// *)
	
	-- if write successful, convert to MD
	if result = true then
		try
			--use Python script to convert HTML to MD
			set mmd to do shell script "python " & (quoted form of html_processor) & space & (quoted form of html_target)
			
			--prepare MMD headers
			set mmd to "# " & _title & "   " & LF & "= " & _notebook & "   " & LF & "@ " & _tags & "   " & LF & LF & LF & mmd
			
			--write MD text to storage file
			set md_target to (storage_path & _title & ".md")
			my write_to_file(mmd, md_target, false)
			
			--if write successful, open MD file
			if result = true then
				do shell script "open " & (quoted form of md_target)
			end if
			
			tell application "Finder" to delete ((POSIX file html_target) as alias)
			
		on error err number num
			error err number num
		end try
	end if
end run

(* HANDLERS *)

on get_base_path()
	set {tid, AppleScript's text item delimiters} to {AppleScript's text item delimiters, "/"}
	set _path to (text items 1 thru -2 of (POSIX path of (path to me)) as string) & "/"
	set AppleScript's text item delimiters to tid
	return _path
end get_base_path

to join_list(aList, delimiter)
	set retVal to ""
	set prevDelimiter to AppleScript's text item delimiters
	set AppleScript's text item delimiters to delimiter
	set retVal to aList as string
	set AppleScript's text item delimiters to prevDelimiter
	return retVal
end join_list

on remove_from_string(theText, CharOrString)
	-- ljr (http://applescript.bratis-lover.net/library/string/)
	local ASTID, theText, CharOrString, lst
	set ASTID to AppleScript's text item delimiters
	try
		considering case
			if theText does not contain CharOrString then ¬
				return theText
			set AppleScript's text item delimiters to CharOrString
			set lst to theText's text items
		end considering
		set AppleScript's text item delimiters to ASTID
		return lst as text
	on error eMsg number eNum
		set AppleScript's text item delimiters to ASTID
		error "Can't remove_from_string: " & eMsg number eNum
	end try
end remove_from_string

on write_to_file(this_data, target_file, append_data)
	try
		set the target_file to the target_file as string
		try
			set the open_target_file to open for access file target_file with write permission
		on error
			set the open_target_file to open for access POSIX file target_file with write permission
		end try
		if append_data is false then set eof of the open_target_file to 0
		write (this_data) to the open_target_file starting at eof as «class utf8»
		close access the open_target_file
		return true
	on error
		try
			close access file target_file
		end try
		return false
	end try
end write_to_file