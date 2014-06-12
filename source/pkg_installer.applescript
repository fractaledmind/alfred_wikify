on run
	--get path to current directory
	set base_path to my get_base_path()
	
	--prepare path to Python converter script
	set satimage_pkg to base_path & "Satimage392.pkg"
	
	set sResult to do shell script "xattr -dr com.apple.quarantine '" & satimage_pkg & "'"
	do shell script "sleep 0.2"
	do shell script "open " & satimage_pkg & " -a Installer"
	
end run

on get_base_path()
	set {tid, AppleScript's text item delimiters} to {AppleScript's text item delimiters, "/"}
	set _path to (text items 1 thru -2 of (POSIX path of (path to me)) as string) & "/"
	set AppleScript's text item delimiters to tid
	return _path
end get_base_path