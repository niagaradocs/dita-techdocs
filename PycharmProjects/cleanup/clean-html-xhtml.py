#!/usr/bin/env python3
#!/usr/local/bin

import re
import os
import shutil

doc = input('Enter a document name:  ')
drc = f'c:/niagara/r4dev/techdocs_dev/docs/{doc}/{doc}-doc/src/doc'
backuph = 'c:/niagara/backups/html/{}'.format(doc)
backupx = 'c:/niagara/backups/xhtml/{}'.format(doc)
pattern = re.compile('<!.*DOCTYPE html') #HTML Pattern
patternx = re.compile('<\?xml version="1.0" encoding="UTF-8"\?>') #XHTML Pattern
p = re.compile('<script[\s\S]*css">\n') #javascript and css links
# --------- html search variables ---------------
a_str = 'style="max-width: 100%; "'
b_str = '<br>'
n_str = ''
r_str = '\n'
#------------- Files and folders variables ------------------------
delete_file = ['banner.html', 'default.htm', 'frame_main.html', 'frame_nav.html', 'frame_tabs.html', 'frame_views.html', 'tabs.html', 'toolbar_index_term.html', 'toolbar_toc.html', 'view_index_term.html', 'view_profile.html', 'views.html']
delete_folder = ['css', 'images', 'javascript']
rename_file = ['view_toc.html']
#======== delete files and folders ============
for file in(delete_file):
    if os.path.exists(os.path.join(drc, file)):
        os.remove(os.path.join(drc, file))
        print(file, "file deleted")
    else:
        print(file, "file does not exist")
for folder in(delete_folder):
    if os.path.isdir(os.path.join(drc, folder)):
        shutil.rmtree(os.path.join(drc, folder))
        print(folder, "folder deleted")
    else:
        print(folder, "not found")
try:
    os.makedirs(backuph)
except OSError:
    print ("Creation of the directory %s failed or already exists" % backuph)
else:
    print ("Successfully created the backup directory %s" % backuph)   
# ------------- Create Backup, Search and replace ----------------------------    
for dirpath, dirname, filename in os.walk(drc):#Getting a list of the full paths of files
    for fname in filename:
        path = os.path.join(dirpath, fname) #Joining dirpath and filenames
        with open(path, encoding='utf-8', errors='ignore') as f:
            strg = f.read()#Opening the files for reading only
        if re.search(pattern, strg):#If we find the pattern for html
            shutil.copy2(path, backuph) #we will create a backup of it
            strg = strg.replace(a_str, n_str) #replace a_str (max width)
            strg = strg.replace(b_str, n_str) #replace br tags of all varieties
            result = re.search(p, strg)
            if result:
                strg = strg.replace(result.group(0), r_str) #remove javascript and css links
                print (result.group(0))
# ---------------- Rename the toc file ----------------    
for rname in (rename_file):
    if os.path.isfile(os.path.join(drc, rname)):
        os.rename(os.path.join(drc, rname), os.path.join(drc, 'toc.xml'))
        print(rname, 'renamed to toc.xml')
    else:
        print(rname, "file does not exist")
# -------------  write and close files --------------------  
        #else: print(patternh, "does not exist")
    f = open(path, 'w', encoding="utf-8") #We open the files with the WRITE option
    f.write(strg) # We are writing the the changes to the files
    f.close() #Closing the filesfor rname in(rename_file):
    
