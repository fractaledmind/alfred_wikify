
(*
http://veritrope.com
Evernote -- Empty Tag Remover
Version 1.0
December 22, 2010
Project Status, Latest Updates, and Comments Collected at:
http://veritrope.com/code/evernote-empty-tag-remover
*)

property unusedTags : {}

on run
	set unusedTags to {}
	
	tell application id "com.evernote.Evernote"
		try
			set theTags to every tag
			repeat with theTag in theTags
				set theNotes to {}
				set theName to "\"" & name of theTag & "\""
				set theNotes to (find notes "tag:" & theName)
				if theNotes is {} then
					copy theName to the end of unusedTags
					delete tag (name of theTag)
				end if
			end repeat
		end try
		set sortedTags to my simple_sort(unusedTags)
		set oldDelim to AppleScript's text item delimiters
		set AppleScript's text item delimiters to return
		set sortedList to sortedTags as text
		set AppleScript's text item delimiters to oldDelim
		
		set n to create note with text sortedList title "Deleted Tags"
	end tell
end run

--SORT SUBROUTINE
on simple_sort(my_list)
	set the index_list to {}
	set the sorted_list to {}
	repeat (the number of items in my_list) times
		set the low_item to ""
		repeat with i from 1 to (number of items in my_list)
			if i is not in the index_list then
				set this_item to item i of my_list as text
				if the low_item is "" then
					set the low_item to this_item
					set the low_item_index to i
				else if this_item comes before the low_item then
					set the low_item to this_item
					set the low_item_index to i
				end if
			end if
		end repeat
		set the end of sorted_list to the low_item
		set the end of the index_list to the low_item_index
	end repeat
	return the sorted_list
end simple_sort