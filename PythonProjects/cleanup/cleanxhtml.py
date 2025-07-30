#!/usr/bin/env python3
#!/usr/local/bin
import fnmatch
import time
import re
import os
import shutil
import subprocess
import sys
# this file works on single documents to clean xhtml files and initiate a build for that file. Using environment
# variables in the dita-ot plugin requires that you use quotes around the file paths specified in environment varialbes

doc = input('Enter a document name:  ')
#drc = f'c:/niagara/r4dev/techdocs_dev/docs/{doc}/{doc}-doc/src/doc/'
drcx = f'c:/Users/E333758/Honeywell/Tridium Tech Docs - Resource Center - bundles_sources/Source_xhtml_N4/{doc}/'
toc = f'c:/Users/E333758/Honeywell/Tridium Tech Docs - Resource Center - bundles_sources/Source_xhtml_N4/{doc}/view_toc.html'
bat = f'c:/Users/E333758/Honeywell/Tridium Tech Docs - Resource Center - bundles_sources/Source_xhtml_N4/{doc}.bat'

#drcx = f'c:/niagara/r4dev/techdocs_dev/docs/{doc}/{doc}-doc/src/doc/'
backuph = 'c:/niagara/backups/html/{}'.format(doc)
backupx = 'c:/niagara/backups/xhtml/{}'.format(doc)
pattern = re.compile('<!.*DOCTYPE html') #HTML Pattern
patternx = re.compile('<\?xml version="1.0" encoding="UTF-8"\?>') #XHTML Pattern
p = re.compile('#styler-idu?1.*?"') #hashtag stuff from toc
# --------- html search variables ---------------
#a_str = 'style="max-width: 100%; "'
b_str = '<br />'
c_str = '<br class="empty" />'
n_str = ''
q_str = '"'
r_str = '\n'
#------------- Files and folders variables ------------------------
delete_file = ['banner.html', 'default.htm', 'frame_main.html', 'frame_nav.html', 'frame_tabs.html', 'frame_views.html', 'tabs.html', 'toolbar_index_term.html', 'toolbar_toc.html', 'view_index_term.html', 'view_profile.html', 'views.html']
delete_folder = ['css', 'images', 'javascript']
toc = ['view_toc.html']
#======== delete files and folders ============
for file in(delete_file):
    if os.path.exists(os.path.join(drcx, file)):
        os.remove(os.path.join(drcx, file))
        print(file, "file deleted")
    else:
        print(file, "file does not exist")
for folder in(delete_folder):
    if os.path.isdir(os.path.join(drcx, folder)):
        shutil.rmtree(os.path.join(drcx, folder))
        print(folder, "folder deleted")
    else:
        print(folder, "not found")
# ------------- Create Backup, Search and replace ----------------------------    
for dirpath, dirname, filename in os.walk(drcx):#Getting a list of the full paths of files
    for fname in filename:
        path = os.path.join(dirpath, fname) #Joining dirpath and filenames
        if fname.endswith('.html'):
            with open(path, encoding='utf-8', errors='ignore') as f:
                strg = f.read()#Opening the files for reading only
            #if re.search(#styler-idu?1.*?", strg):#If we find the pattern for xhtml
                #shutil.copy2(path, backupx) #we will create a backup of it
                strg = strg.replace(b_str, n_str) #replace br tags
                strg = strg.replace(c_str, n_str) #replace h)
                # --------------- get the hashtag stuff -------------------
                strg = re.sub(p, q_str, strg)
# -------------  write and close files --------------------  
            f = open(path, 'w', encoding="utf-8") #We open the files with the WRITE option
            f.write(strg) # We are writing the changes to the files
            f.close() #Closing the filesfor rname in(rename_file):
# ---------------- pause [I don't think this is accomplishing anything ---------------
print("Complete")
#time.sleep(5)
# ---------------- run classification batch file --------------------------------
#subprocess.run([bat])
run = input('Run Classification file? yes/no:  ')
if run == 'yes':
    subprocess.run([bat])
else:
    print('Finished')
