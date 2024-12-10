import os
import shutil
import zipfile

def find_and_unzip_files(source_root, doc_folder_name):
    """Find zip files matching doc_folder_name and unzip all contents into its own folder."""
    zip_files = [f for f in os.listdir(source_root) if f.endswith('.zip') and f.startswith(doc_folder_name)]
    if not zip_files:
        print(f"No zip files found in {source_root} with the prefix '{doc_folder_name}'.")
        return None

    doc_folder_path = os.path.join(source_root, doc_folder_name)
    os.makedirs(doc_folder_path, exist_ok=True)

    for zip_file in zip_files:
        zip_file_path = os.path.join(source_root, zip_file)
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(doc_folder_path)
        print(f"Extracted contents from {zip_file} to {doc_folder_path}.")
    return doc_folder_path

def copy_and_rename_index(renamed_folder_path, target_root_folder):
    """Copy and rename index.html to toc.html."""
    index_path = os.path.join(renamed_folder_path, 'index.html')
    toc_path = os.path.join(target_root_folder, 'toc.html')

    if not os.path.exists(index_path):
        print(f"Error: 'index.html' not found in {renamed_folder_path}.")
        return

    os.makedirs(target_root_folder, exist_ok=True)

    try:
        shutil.copy(index_path, toc_path)
        print(f"Copied and renamed 'index.html' to 'toc.html' in {target_root_folder}")
    except Exception as e:
        print(f"Error copying and renaming 'index.html' to 'toc.html': {e}")

def copy_images(source_path, target_path):
    """Copy all images from 'graphic' to 'graphics'."""
    graphic_folder = os.path.join(source_path, "graphic")
    graphics_folder = os.path.join(target_path, "graphics")
    os.makedirs(graphics_folder, exist_ok=True)

    if os.path.exists(graphic_folder):
        for img_file in os.listdir(graphic_folder):
            src_img_path = os.path.join(graphic_folder, img_file)
            tgt_img_path = os.path.join(graphics_folder, img_file)
            shutil.copy(src_img_path, tgt_img_path)
            print(f"Copied {img_file} to graphics folder.")
    else:
        print(f"Warning: No 'graphic' folder found in {source_path}.")
