# todo.txt-to-Tasks.org-converter
##Python program to convert todo.txt to JSON file for import to Tasks.org Android app
##Overview
If you have lots of tasks in a todo.txt file (e.g. from Simpletask Android app, now mothballed) and want to start using the Android Tasks.org app, it's a pain to add them individually. I wrote this very basic Python program to avoid that (I'm not a programmer, so it's pretty bad Python I'm sure). You'll need to install Python on your system to run it.
##How to use
Download converter_todo_to_tasks.py and place in the same folder as it the following:
(a) An input file todo.txt that contains a list of tasks in Simpletask (Mark Janssen/mpcjanssen) todo notation. 
(b) An input file empty_tasks.json. To create this input, open the Android Tasks.org app (Alex Baker/alex_baker), clear all data (settings > advanced > delete task data), then do a backup (settings > backups > backup now). Find the file, copy and rename.
The tasks in (a) and the surrounding json data of (b) will be combined in a new file new_tasks.json in the same folder. This can be put back in the Tasks.org app backup folder and imported back into the app (settings>backups>backup now). The imported tasks will all be in the local "Default list". They can be moved, tagged etc. in bulk in various ways by long pressing on a task and then using select all.
##Notes 
The code was tested with Simpletask todo.txt, but any todo.txt that doesn't use additional formatting rules should work with it.

I used todo.txt with UTF-8 encoding (set in the editor I saved from - I think this is what Simpletask uses).

Todo.txt needs to be without format/syntax errors or this program will break. Also, it is likely that \ and " will break it - remove them first in a text editor if necessary. I use " for inches, but replaced with '' - which happen to look like " in Tasks app. All other symbols available in Simpletask seem to work OK.

This does not process recurring/repeating todo format of Simpletask into Tasks.org recurring tasks. The syntax is left in the title of the task in Tasks.org.

Each task after the first one in a Tasks.org json has a field "order", a 9 digit number. In short, this doesn't appear to be needed to import todos, so is left out.

In the json there is a 'default_remote_list' number. In an empty json it is different to the (randomly generated) 'calendar' ID number, but the same if there are tasks. It seems the safest way to deal with it is to make it the same. 

BTW I used notepad++ and plugin JSON Viewer 2.0.7.0 whilst developing this- it's 'format JSON' option sometimes didn't work even with correct JSON until notepad++ was restarted.

Credit to dessalines who wrote a converter in Rust and ccoenen gave me some help. (https://github.com/tasks/tasks/issues/2085). The Rust code generates output that can be cut and pasted into a json. The version I tried doesn't process todo "@context" as tags, you can search and replace the @ for + before running it. I didn't understand the Rust code, so I wrote it again in Python which I've been meaning to learn.
