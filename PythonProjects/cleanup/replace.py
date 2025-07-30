#!/usr/bin/env python3
#!/usr/local/bin
import re
import os
import shutil
import subprocess
import sys

doc = input('Enter a document name:  ')
drc = f'c:/niagara/r4dev/techdocs_dev/docs/{doc}/{doc}-doc/src/doc/'
drcx = f'c:/Users/E333758/Honeywell/Tridium Tech Docs - RCLibrary - ResourceCenterFiles/Source_xhtml_N4/{doc}/'
toc = f'c:/Users/E333758/Honeywell/Tridium Tech Docs - RCLibrary - ResourceCenterFiles/Source_xhtml_N4/{doc}/view_toc.html'

pattern = re.compile('<#styler-idu?1.*?"') #Hashtag Pattern
patternx = re.compile('<\?xml version="1.0" encoding="UTF-8"\?>') #XHTML Pattern
p = re.compile('#styler-idu?1.*?"') #hashtag stuff from toc
# --------- html search variables ---------------
#a_str = 'style="max-width: 100%; "'
b_str = '<br />'
n_str = ''
q_str = '"'
r_str = '\n'

with open(toc,'r') as f:
    strg = f.read()
    x = re.sub(p,q_str,strg)
    print(x)
    f = open(toc,'w')
    f.write(x)
    f.close()