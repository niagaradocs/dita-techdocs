#!/usr/bin/env python3
#!/usr/local/bin
# This file cleans published html for workbench help. It is working fine as of May 9, 2021!
import re
import os
import shutil
import subprocess

doc = input('Enter a document name:  ')
src = f"c:/Users/E333758/Honeywell/PUBLIC Tridium Tech Docs - Workbench_Help - Documents/{doc}/"
dst = f"c:/niagara/techdocsdev/docs/{doc}/{doc}-doc/src/doc/"
backuph = 'c:/niagara/backups/html/{}'.format(doc) 
backupx = 'c:/niagara/backups/xhtml/{}'.format(doc)
pattern = re.compile('<!.*DOCTYPE html') #HTML Pattern
patternx = re.compile('<\?xml version="1.0" encoding="UTF-8"\?>') #XHTML Pattern
p = re.compile('<script[\s\S\n\r]*type="text/css">') #javascript and css links
# --------- html search variables ---------------
a_str = 'style="max-width: 100%; "'
b_str = '<br>'
c_str = '<br class="empty">'
n_str = ''
r_str = '\n'
src = '--version'
cmd = 'gradlew'
docjar = f'{doc}:jar'


#------------- Files and folders variables ------------------------
delete_file = ['banner.html', 'default.htm', 'frame_main.html', 'frame_nav.html', 'frame_tabs.html', 'frame_views.html', 'tabs.html', 'toolbar_index_term.html', 'toolbar_toc.html', 'view_index_term.html', 'view_profile.html', 'views.html']
delete_folder = ['css', 'images', 'javascript']
rename_file = ['view_toc.html']
docs = ['docBaaS', 'docBacnet', 'docPlatform', 'docRdbms', 'docAlarms', 'docHistories', 'docDrivers', 'docVideoframework', 'docMqtt', 'docUser', 'docProvisioning', 'docStationSecurity']

#======== cleanup part 1: delete files and folders ============
for file in(delete_file):
    if os.path.exists(os.path.join(dst, file)):
        os.remove(os.path.join(dst, file))
        print(file, "file deleted")
    else:
        print(file, "file does not exist")
for folder in(delete_folder):
    if os.path.isdir(os.path.join(dst, folder)):
        shutil.rmtree(os.path.join(dst, folder))
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
for dirpath, dirname, filename in os.walk(dst):#Getting a list of the full paths of files
    for fname in filename:
        path = os.path.join(dirpath, fname) #Joining dirpath and filenames
        if fname.endswith('.html'):
            with open(path, encoding='utf-8', errors='ignore') as f:
                strg = f.read()#Opening the files for reading only
            if re.search(pattern, strg):#If we find the pattern for html
               #shutil.copy2(path, backuph) #we will create a backup of it
                strg = strg.replace(a_str, n_str) #replace a_str (max width)
                strg = strg.replace(b_str, n_str) #replace br tags 
                strg = strg.replace(c_str, n_str) #replace br tags with class
                #print ('success')
                result = re.search(p, strg)
                if result:
                    strg = strg.replace(result.group(0), r_str) #remove javascript and css links
                    #print (result.group(0))
# -------------  write and close files --------------------  
            f = open(path, 'w', encoding="utf-8") #We open the files with the WRITE option
            f.write(strg) # We are writing the the changes to the files
            f.close() #Closing the filesfor rname in(rename_file):
# ---------------- Rename the toc file ----------------    
for rname in (rename_file):
    if os.path.isfile(os.path.join(dst, rname)):
        os.rename(os.path.join(dst, rname), os.path.join(dst, 'toc.xml'))
        print(rname, 'renamed to toc.xml')
    else:
        print(rname, "file does not exist")
#---------------------- Run Gradlew -------------------------
run = input('Run gradlew? yes/no:  ')
if run == 'yes':
    os.chdir("c:\\niagara\\techdocsdev\\")
    subprocess.run([cmd, docjar], shell=True)
else:
    print('Finished')