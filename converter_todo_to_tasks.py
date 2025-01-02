#! /usr/bin/python
# OVERVIEW
# Place in the same folder as this Python program:
# (a) An input file todo.txt that contains a list of tasks in Simpletask (Mark Janssen/mpcjanssen) todo notation.
# (b) An input file empty_tasks.json. To create this input, open the Tasks.org ap (Alex Baker/alex_baker), clear all data (settings>advanced>delete task data), then do a backup (settings>backups>backup now). Find the file, copy and rename.
# the tasks in (a) and the surrounding json data of (b) will be combined in a new file new_tasks.json in the same folder. This can be put back in the Tasks.org app backup folder and imported back into the app (settings>backups>backup now). The imported tasks will all be in the local "Default list". They can be moved, tagged etc. in bulk in various ways by long pressing on a task and then using select all.
# NOTES
## credit to dessalines who wrote a converter in Rust and ccoenen gave me some help. (https://github.com/tasks/tasks/issues/2085). The Rust code generates output that can be cut and pasted into a json. It doesn't process todo "@context" as tags, so you'd have to search and replace the @ for + before running it. I didn't understand the Rust code, so I wrote it again in Python which I've been meaning to learn.
# this is shoddy code by a newbie using the simplest Python language - apologies.
# I used todo.txt with UTF-8 encoding (set in the editor I saved from - I think this is what Simpletask uses)
# Todo.txt needs to be without errors or this program will break. Also, it is likely that \ and " will break it - remove them first in a text editor if necessary. I use " for inches, but replaced with '' - which happen to look like " in Tasks app. All other symbols available in Simpletask seem to work OK.
# this does not process recurring/repeating todo syntax of Simpletask into Tasks.org recurring tasks. The syntax is left in the title of the task in Tasks.org
# each task after the first one in a Tasks.org json has a field "order", a 9 digit number. In short, this doesn't appear to be needed to import todos, so is left out.
# in the json there is a 'default_remote_list' number. In an empty json it is different to the (randomly generated) 'calendar' ID number, but the same if there are tasks. It seems the safest way to deal with it is to make it the same. 
# used notepad++ and plugin JSON Viewer 2.0.7.0 - it's 'format JSON' option sometimes didn't work even with correct JSON until notepad++ was restarted.
import json
import random
import string #just for string.digit
import re
from pathlib import Path
from datetime import datetime

def read_todo_txt_file():
    #each line is a todo
    print("read_todo_txt_file")
    todos = []
    with open("todo.txt", "r") as file:
        for todo in file:
            #todo is type string
            type(todo)
            todos.append(todo.strip()) #remove any leading and trailing whitespace
    # * prints list in column without "\n","," and [ ])
    n_todos=len(todos)
    return todos,n_todos
    
def parse_task_prefixes_from_todo(todos):
    print("parse_task_prefixes_from_todo")
    is_complete=[] #stores if a todo is already completed
    priority=[] #stores the todo priority (to be converted to a Tasks.org priority later)
    complete=[] #stores completion date
    create=[] #stores creation date
    n=0
    #for the first section of todo I need to partly rely on position in line to identify
    todo_prefix=[0]*len(todos) #no. of characters used up by completed, priorities, dates
    for todo in todos:
        #todo is complete:
        if todo[0] == 'x':
            is_complete.append(1)
            todo_prefix[n]=2
            #and has a priority:
            if todo[2] + todo[4] == '()' and re.match('[A-Z]',todo[3]):
                priority.append(todo[3])
                #so completion date is here
                complete.append(todo[6:16])
                todo_prefix[n]=17
                #and has a create date:
                if todo[21]+todo[24]=='--' and re.match('[0-9]{8,8}',todo[17:21]+todo[22:24]+todo[25:27]):
                    create.append(todo[17:27])
                    todo_prefix[n]=28
                #and doesn't have a create date:
                else:
                    create.append('')
            #and has no priority (completion is in different position):
            else:
                priority.append('')
                complete.append(todo[2:12])
                todo_prefix[n]=13
                #and has a create date:
                if todo[17]+todo[20]=='--' and re.match('[0-9]{8,8}',todo[13:17]+todo[18:20]+todo[21:23]):
                    create.append(todo[13:23])
                    todo_prefix[n]=24
                #and doesn't have a create date:
                else:
                    create.append('')
        #todo is not complete:
        else:
            is_complete.append(0)
            complete.append('')
            todo_prefix[n]=0
            #and has a priority:
            if todo[0] + todo[2] == '()' and re.match('[A-Z]',todo[1]):
                priority.append(todo[1])
                todo_prefix[n]=4
                #and has a create date:
                if todo[8]+todo[11]=='--' and re.match('[0-9]{8,8}',todo[4:8]+todo[9:11]+todo[12:14]):
                    create.append(todo[4:14])
                    todo_prefix[n]=15
                #and doesn't have a create date:
                else:
                    create.append('')
            #and has no priority:
            else:
                priority.append('')
                #and has a create date:
                if todo[4]+todo[7]=='--' and re.match('[0-9]{8,8}',todo[0:4]+todo[5:7]+todo[8:10]):
                    create.append(todo[0:10])
                    todo_prefix[n]=10
                #and doesn't have a create date:
                else:
                    create.append('')
        n=n+1
    return todos,todo_prefix,is_complete,complete,create,priority

def parse_task_titles_projects_contexts_due_threshold(todos,todo_prefix):
    print('parse_task_titles_projects_contexts_due_threshold')
    tags=[]
    titles=[]
    due=[]
    threshold=[]
    n=0
    for todo in todos:
        todo=todo[todo_prefix[n]:] #remove prefixes
        parts=todo.split() #split the rest at blank spaces
        todo_tags=[]
        todo_title=[]
        todo_due=''
        todo_threshold=''
        m=0
        for part in parts[:]: #loop over a copy so I can delete part from parts list
            if  (part[0]=='@' or part[0]=='+') and len(part)>1: #turn @context and +project into tags
                #and len(part)>1 avoids a single + or @ being turned into a tag
                todo_tags.append(part)
                del parts[m] #parts list shrinks by 1 each time, so m stays the same 
            elif part[0:4]=='due:':
                todo_due=todo_due+(part[4:14])
                del parts[m] #parts list shrinks by 1 each time, so m stays the same 
            elif part[0:2]=='t:':
                todo_threshold=todo_threshold+(part[2:12])
                del parts[m] #parts list shrinks by 1 each time, so m stays the same 
            else:
                m=m+1 #parts list stays the same, so need to move on 1
        tags.append(todo_tags)
        todo_title=' '.join(parts)
        titles.append(todo_title)
        due.append(todo_due)
        threshold.append(todo_threshold)
        n=n+1
    return(todos,tags,titles,due,threshold)
    
def priority_convert(priority):
    print('priority_convert')
    priority_tasks=[]
    for p in priority:
        if  p == 'A':
            priority_tasks.append(0)
        elif p == 'B':
            priority_tasks.append(1)
        elif p == 'C':
            priority_tasks.append(2)
        elif re.match('[D-Z]',p) or p=='':
            priority_tasks.append(None)
    return(priority_tasks)

def to_unix_time(n_todos,complete,create,due,threshold):
    print('to_unix_time')
    #get unix time for Tasks.org from todo dates
    #adjust to be midday to avoid GMT/BST possible data errors
    #convert to millisecs
    complete_unix=create_unix=due_unix=threshold_unix=[]
    #make input list of lists to combine 4 loops
    dates=[complete, create, due, threshold]
    #make output empty list of lists to combine 4 loops
    #other methods result in copies of lists, not new lists, beware!
    times_unix = [[0]*n_todos for n in range(4)]
    i=0
    for i in range(0,4): #loop complete, create, due, threshold
        j=0
        for j in range(0,n_todos):
            unix_temp=time_unix=0
            date=dates[i][j]
            if date=='':
                time_unix=None
            else:
                unix_temp=(datetime.fromisoformat(date)).timestamp()
                time_unix=(int((unix_temp+43200)*1000)) #43200 secs is 12 hour midday correction
            times_unix[i][j]=time_unix
    #create individual lists from unix_temp for the different date types
    complete_unix=times_unix[0]
    create_unix=times_unix[1]
    due_unix=times_unix[2] 
    threshold_unix=times_unix[3]
    now_unix=int(datetime.now().timestamp() * 1000) #if todo has no creation date (simpletask allows that)
    return complete_unix, create_unix, due_unix, threshold_unix, now_unix
    
def make_tagUid(tags):
    print('make_tagUid')
    #need an ID for each unique tag, but only have a list of tags for each task, full of duplicates
    #take all tags from list of lists "tag" and put in flat_tags
    flat_tags=[]
    for task in tags:
        for tag in task:
            flat_tags.append(tag)
    #now create a dictionary with the tags as 'keys' - this eliminates duplicates
    tagUid = dict.fromkeys(flat_tags)
    #add random IDs as dictionary 'values' to allow lookup of an ID number for each tag
    #population=string.digits=0 to 9; no. of digits=k=19;''.join=join them all together with no gaps
    for tag, ID in tagUid.items():
        tagUid[tag] = ''.join(random.choices(string.digits,k=19))  
    return tagUid
    
def output_str(titles,priority_tasks,is_complete,complete_unix,create_unix,due_unix,threshold_unix,now_unix,tags,tagUid):
    print('output_str')
    #create string 'output' for json, adding to it as we progress
    #create one "calendar" ID number: population=string.digits=0 to 9; no. of digits=k=19; ''.join=join them all together with no gaps
    calendar=''.join(random.choices(string.digits,k=19))      
    #create string for tasks part of json
    i=0
    output='{"tasks": [' #opening for tasks part of json
    #loop through all tasks:
    for i in range(0,len(titles)): 
        output=output+'{"task":' + '{"title"'+':' + '"'+str(titles[i])+'"' #open each task and title block
        if priority_tasks[i]!=None:
           output=output+',"priority":'+str(priority_tasks[i])
        if due_unix[i]!=None:
           output=output+',"dueDate":'+str(due_unix[i])
        if threshold_unix[i]!=None:
           output=output+',"hideUntil":'+str(threshold_unix[i])
        if create_unix[i]!=None:
           output=output+',"creationDate":'+str(create_unix[i])
           output=output+',"modificationDate"'+':'+str(create_unix[i])
        else:
           output=output+',"creationDate":'+str(now_unix)
           output=output+',"modificationDate":'+str(now_unix)
        if complete_unix[i]!=None:
           output=output+',"completionDate":'+str(complete_unix[i])
        #create unique ID for each task: population=string.digits=0 to 9; no. of digits=k=19; ''.join=join them all together with no gaps
        task_remoteId=''.join(random.choices(string.digits,k=19))
        output=output+',"remoteId":'+'"'+str(task_remoteId)+'"'
        output=output+'},' #close task title block
        #alarm field is only populated if a due date is present
        if due_unix[i]!=None:
           output=output+'"alarms":[{"type":'+str(2)+'}],'
        else:
           output=output+'"alarms":[],'
        output=output+'"geofences": [],'
        #create tags for each task
        output=output+'"tags": ['
        #print(f"length of tags:{len(tags[i])}")
        if tags[i]!=[]:
            for t in range(0,len(tags[i])): #t starts at 0 to use for indexing
                #tags[i][t][1:] is the i-th 'column' of the outer list, the t-th 'row', all letters bar the first in that element:
                output=output+'{"name":"'+tags[i][t][1:]+'","tagUid":"'+tagUid[tags[i][t]]+'"}'
                if t+1<len(tags[i]): #if it's not the last tag for that task, add a comma
                   output=output+','
        output=output+'],' #close tags for each task
        output=output+'"comments": [],'+'"attachments": [],' 
        #create unique CalDAV ID for the task: population=string.digits=0 to 9; no. of digits=k=19; 
        #''.join=join them all together with no gaps
        calendar_remoteId=''.join(random.choices(string.digits,k=19))        
        output=output+'"caldavTasks":[{"calendar":"'+str(calendar)+'","remoteId": "'+str(calendar_remoteId)+'"}]'
        if i==len(titles)-1: #close task if last one
            output=output+'}'
        else:
            output=output+'},' #close task with comma if more tasks to come
    output=output+'],' #close tasks
    #misc. json part incl. tags part of json
    output=output+'"places": [],'
    output=output+'"tags": ['
    k=0
    for tag, ID in tagUid.items():
        output=output+'{"remoteId":"'+str(ID)+'","name":"'+str(tag[1:])+'"}'
        if k+1<len(tagUid):
            output=output+','
        k=k+1
    output=output+'],'
    output=output+'"filters": [],'
    output=output+'"caldavAccounts": [{"uuid": "local","accountType": 2}],'
    output=output+'"caldavCalendars":[{"account":"local","uuid": "'+str(calendar)+'","name": "Default list"}]'
    #output.json is just for debugging, it is the new stuff from todo.text that will be combined with the Tasks empty backup JSON. If you open it in an editor add } to end of it, it should display as formatted json if the program is working and the editor supports json:
    #Path('output.json').write_text(output)
    return output,calendar
    
def new_json_file(output,calendar):
    print('new_json_file')
    #read existing json, create new one with added todo tasks, tags, calendar miscellany, and changed "default_remote_list ID number"
    #'empty_tasks.json' is a single line file, so no line loop required
    with open("empty_tasks.json", "r") as file:
        tasks_json=file.read()
    tasks_json=tasks_json.replace('"default_remote_list":"4:2280471098339662788"','"default_remote_list":"4:'+str(calendar)+'"')
    #use regular expression to find bit of empty json I want to replace
    #everything between (and including) {"tasks": and "Default list"}]
    print(output)
    tasks_json=re.sub('{"tasks":.*?"Default list"}]',str(output), tasks_json, flags=re.DOTALL)
    #open, or create if required, output json:
    file = open("new_tasks.json", "w")
    file.write(tasks_json)
    file.close
    return

def main():
    todos,n_todos = read_todo_txt_file()
    todos,todo_prefix,is_complete,complete,create,priority = parse_task_prefixes_from_todo(todos)
    todos,tags,titles,due,threshold = parse_task_titles_projects_contexts_due_threshold(todos,todo_prefix)
    priority_tasks=priority_convert(priority)
    complete_unix,create_unix,due_unix,threshold_unix,now_unix=to_unix_time(n_todos, complete, create, due, threshold)
    tagUid=make_tagUid(tags)
    output,calendar=output_str(titles,priority_tasks,is_complete,complete_unix,create_unix,due_unix,threshold_unix,now_unix,tags,tagUid)
    new_json_file(output,calendar)

if __name__ == "__main__":
    main()