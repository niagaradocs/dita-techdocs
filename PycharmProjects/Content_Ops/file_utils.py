# file_utils.py
import os
import shutil
import zipfile

def find_and_unzip_files(source_root, doc_folder_name):
    """Find zip files matching doc_folder_name and unzip only html5 contents into its own folder."""
    zip_files = [f for f in os.listdir(source_root) if f.endswith('.zip') and f.startswith(doc_folder_name)]

    if not zip_files:
        print(f"No zip files found in {source_root} with the prefix '{doc_folder_name}'.")
        return None

    doc_folder_path = os.path.join(source_root, doc_folder_name)
    os.makedirs(doc_folder_path, exist_ok=True)

    for zip_file in zip_files:
        zip_file_path = os.path.join(source_root, zip_file)

        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                if member.startswith('ot-output/html5/'):
                    target_path = os.path.join(doc_folder_path, member.replace('ot-output/html5/', '', 1))
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with zip_ref.open(member) as source, open(target_path, "wb") as target:
                        shutil.copyfileobj(source, target)

            print(f"Extracted contents of 'html5' from {zip_file} to {doc_folder_path}.")

    return doc_folder_path

def copy_and_rename_index(renamed_folder_path, target_root_folder):
    """Copy and rename index.html to toc.html."""
    index_path = os.path.join(renamed_folder_path, 'index.html')
    if os.path.exists(index_path):
        toc_path = os.path.join(target_root_folder, 'toc.html')
        shutil.copy(index_path, toc_path)
        print(f"Copied and renamed 'index.html' to 'toc.html' in {target_root_folder}")

# You can add other functions related to file handling here, like `remove_unnecessary_images`, `copy_images`, etc.
