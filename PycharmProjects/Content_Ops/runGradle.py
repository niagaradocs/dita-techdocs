#!/usr/bin/env python3

import os
import subprocess

def run_gradle_for_documents(documents):
    """Run the gradle jar process for each document in the provided list."""
    os.chdir("c:\\niagara\\techdocsdev\\")
    cmd = 'gradlew'
    src = '--version'

    for doc in documents:
        docjar = f'{doc}:jar'
        print(f"Running gradle for document: {doc}")
        subprocess.run([cmd, docjar], shell=True)

if __name__ == "__main__":
    # Ask for document name or use a list
    use_doc_list = input("Use document list? (y/n): ").strip().lower()
    if use_doc_list == 'y':
        documents = input("Enter the list of document names, separated by commas: ").strip().split(',')
        documents = [doc.strip() for doc in documents]
    elif use_doc_list == 'n':
        doc = input("Enter a document name: ").strip()
        documents = [doc]
    else:
        print("Invalid option selected. Exiting.")
        exit(1)

    # Run gradle for each document in the list
    run_gradle_for_documents(documents)
