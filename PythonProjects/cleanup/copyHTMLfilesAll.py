#!/usr/bin/env python3
# !/usr/local/bin
from pathlib import Path
import re
import os
import shutil

# This script deletes the old target folder content and then copies new files to same folder name.

#doc = input('Enter a document name:  ')
docs = ['docDrivers', 'docNSnmp', 'docAnalytics', 'docEdge10Startup', 'docNCloud']
#docs = ['docBaaS', 'docBacnet', 'docPlatform', 'docRdbms', 'docAlarms', 'docHistories', 'docDrivers', 'docVideoframework', 'docMqtt', 'docUser', 'docProvisioning', 'docStationSecurity']
i = 0
for doc in (docs):
    i += 1
    src = f"c:/Users/E333758/Honeywell/Tridium Tech Docs - Workbench_Help - Documents/{doc}/"
    dst = f'c:/niagara/techdocsdev/docs/{doc}/{doc}-doc/src/doc/'
    if os.path.exists(dst):
        shutil.rmtree(dst)
    else:
        print('doc folder not found')
    shutil.copytree(src, dst)
    print('All ' + doc + ' files copied. Total docs copied = ' + str(i))
