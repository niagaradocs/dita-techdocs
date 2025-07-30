#!/usr/bin/env python3
# !/usr/local/bin
from pathlib import Path
import re
import os
import shutil

# This script deletes any existing target folder content and then copies new files to same folder name.

doc = input('Enter a document name:  ')
#docs = ['docBaaS']
# docs = ['docBaaS', 'docBacnet', 'docPlatform', 'docRdbms', 'docAlarms', 'docHistories']
src = f"c:/Users/E333758/Honeywell/PUBLIC Tridium Tech Docs - Workbench_Help - Documents/{doc}/"
dst = f'c:/niagara/techdocsdev/docs/{doc}/{doc}-doc/src/doc/'

for doc in doc:
    if os.path.exists(dst):
        shutil.rmtree(dst)
    else:
        print('doc folder not found')
    shutil.copytree(src, dst)
    print('new files copied')
