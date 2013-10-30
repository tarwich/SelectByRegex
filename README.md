Select By Regex
===============
This Sublime Text 3 plugin will prompt you for a regular expression, then create multiple selections from all of the matches to that regular expression. The range of the search is limited to the current selection. If nothing is selected, then the this command will imply the current line.

Example:
--------
This, is, an, example

 # Select By Regex: ,

This[,] is[,] an[,] example

Usage:
------
After installing, use the command palette and search for "Select By Regex". This brings up the Regex input box at the bottom of the screen. Type in a regular expression and press ENTER, or ESCAPE to cancel.

This can be very useful for splitting a line by commas. You can run the command, then press RIGHT and your cursor(s) will be after every comma. Then just press ENTER.

Keybind:
--------
To bind this to a key, enter the following in your user keybinds file:

````json
{
    "keys": ["super+alt+shift+f"], "command": "select_by_regex",
}
````

Credits:
--------
Special thanks to [klorenz](https://github.com/klorenz) for helping with the ST2 compatibility.
