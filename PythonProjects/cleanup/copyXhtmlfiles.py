#!/usr/bin/env python3
# !/usr/local/bin
from pathlib import Path
import re
import os
import shutil

# This script copies 'custom.properties' and '*.pdf' from target folder to staging folder then deletes
# target folder content and copies files from staging to same folder name in xhtml_source files folder.

doc = input('Enter a document name:  ')
src = f'c:/Users/E333758/Honeywell/Tridium Tech Docs - Resource Center - bundles_sources/_Staging/{doc}/'
dst = f'c:/Users/E333758/Honeywell/Tridium Tech Docs - Resource Center - bundles_sources/Source_xhtml_N4/{doc}/'
pdf = f'c:/Users/E333758/Honeywell/Tridium Tech Docs - Resource Center - bundles_sources/Source_xhtml_N4/{doc}/{doc}.pdf'
cst = f'c:/Users/E333758/Honeywell/Tridium Tech Docs - Resource Center - bundles_sources/Source_xhtml_N4/{doc}/custom.properties'

shutil.copy(cst, src)
shutil.copy(pdf, src)
print(src)

if os.path.exists(dst):
    shutil.rmtree(dst)
else:
    print('folder not found')
shutil.copytree(src, dst)
print('new files copied')
