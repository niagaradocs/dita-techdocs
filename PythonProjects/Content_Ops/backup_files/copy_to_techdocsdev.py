#  NO NEED TO USE THIS IF USING "CombinedProcessHtmlHelp_doc.py" or similar
#  This script copies files from the "c:\_target_html" folder (have been downloaded and processed for Workbench Help)
#  Copies them to the niagara/techdocsdev folder where they will be used to create jar files for sanity check


import os
import shutil

def copy_files(doc_folder_name):
    # Define source and destination paths
    source_path = os.path.join(r'C:\_target_html', doc_folder_name)
    destination_path = os.path.join(r'C:\niagara\techdocsdev', 'docs', doc_folder_name, f'{doc_folder_name}-doc',
                                    '../../cleanup/src',
                                    'doc')

    # Check if the source folder exists
    if not os.path.exists(source_path):
        print(f"Source folder '{source_path}' does not exist. Please check the folder name.")
        return

    # Check if the destination folder exists, and if not, create it
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)
    else:
        # Delete existing files in the destination folder
        for filename in os.listdir(destination_path):
            file_path = os.path.join(destination_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Remove the file
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Remove the folder
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

    # Copy files and subfolders from source to destination folder
    try:
        shutil.copytree(source_path, destination_path, dirs_exist_ok=True)
        print(f"Successfully copied '{doc_folder_name}' and its contents to '{destination_path}'.")
    except Exception as e:
        print(f"Failed to copy '{doc_folder_name}'. Reason: {e}")


if __name__ == '__main__':
    while True:
        doc_folder_name = input("What document do you want to copy to the techdocsdev folder? ")
        copy_files(doc_folder_name)

        # Ask the user if they want to copy another document
        another = input("Copy another document? y/n: ").strip().lower()
        if another != 'y':
            print("Process finished.")
            break