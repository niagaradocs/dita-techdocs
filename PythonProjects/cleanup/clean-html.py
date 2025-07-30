#!/usr/bin/env python3
#!/usr/local/bin
# Copyright 2009-2017 BHG http://bw.org/

import re
import os
import shutil

doc = input('Enter a document name:  ')
drc = f'c:/niagara/techdocsdev/docs/{doc}/{doc}-doc/src/doc'
backup = 'c:/niagara/backups/html/{}'.format(doc)
backup2 = 'c:/niagara/backups/xhtml/{}'.format(doc)
pattern = re.compile('<!.*DOCTYPE html')
pattern2 = re.compile('<\?xml version="1.0" encoding="UTF-8"\?>')
pattern3 = re.compile('<script[\s\S]*css">')

# --------- html search variables ---------------
a_str = ('<script.*>[\s\S]*</script>[\s\S]*<link[\s\S]*css">')
b_str = 'style="max-width: 100%; "'
# --------- xhtml search variables ---------------
c_str = re.compile('#styler-idu?1[^"]*"')
d_str = re.compile('<br\s?/?>')
# --------- replacement variables ---------------
n_str = '' #empty string
q_str = '"' #single ending quote
#------------- Delete files and folders variables ------------------------
delete_file = ['banner.html', 'default.htm', 'frame_main.html', 'frame_nav.html', 'frame_tabs.html', 'frame_views.html', 'tabs.html', 'toolbar_index_term.html', 'toolbar_toc.html', 'view_index_term.html', 'view_profile.html', 'views.html']
delete_folder = ['css', 'images', 'javascript']
rename_file = ['view_toc.html']
         
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
    os.makedirs(backup)
except OSError:
    print ("Creation of the directory %s failed or already exists" % backup)
else:
    print ("Successfully created the backup directory %s" % backup)
    
#-------------- search and replace all items ---------------------------
for dirpath, dirname, filename in os.walk(drc):#Getting a list of the full paths of files
    for fname in filename:
        path = os.path.join(dirpath, fname) #Joining dirpath and filenames
        with open(path, encoding='utf-8', errors='ignore') as f:
            strg = f.read()#Opening the files for reading only
        if re.search(pattern, strg):#If we find the pattern for html only
            print('found it') #print path, contents
            shutil.copy2(path, backup) #we will create a backup of it
            #strg = strg.replace(x, y) #replace a_str
            strg = strg.replace(a_str, n_str) #replace a_str
            strg = strg.replace(b_str, n_str) #replace b_str (max width)
       #else: print(pattern, "does not exist")
#== rename toc file ===       
for rname in(rename_file):
    if os.path.isfile(os.path.join(drc, rname)):
        os.rename(os.path.join(drc, rname), os.path.join(drc, 'toc.xml'))
        print(rname, 'renamed to toc.xml')
    else:
        print(rname, "file does not exist")

#        if re.search(pattern2, strg): #If we find 'pattern2' for xhtml (also need to remove )
#           shutil.copy2(path, backup2) #We create a backup in xhtml folder 
#          strg = strg.replace(c_str, q_str) #replace c_str (styler stuff) with single "
#         strg = strg.replace(d_str, n_str) #replace <br> and <br /> tags
        f = open(path, 'w', encoding="utf-8") #We open the files with the WRITE option
        f.write(strg) # We are writing the the changes to the files
        f.close() #Closing the files
# =========== Job Complete" ===============
print('........... Job Complete ............')