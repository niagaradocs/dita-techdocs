# file_utils.py
import re
import os
import shutil
import zipfile
from bs4 import BeautifulSoup

def find_and_unzip_files(source_root, doc_folder_name):
    '''Find zip files matching doc_folder_name and unzip only html5 contents into its own folder.'''
    zip_files = [f for f in os.listdir(source_root) if f.endswith('.zip') and f.startswith(doc_folder_name)]

    if not zip_files:
        print(f'No zip files found in {source_root} with the prefix \'{doc_folder_name}\'.')
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
                    with zip_ref.open(member) as source, open(target_path, 'wb') as target:
                        shutil.copyfileobj(source, target)

            print(f'Extracted contents of \'html5\' from {zip_file} to {doc_folder_path}.')

    return doc_folder_path

def copy_and_rename_index(renamed_folder_path, target_root_folder):
    '''Copy and rename index.html to toc.html.'''
    index_path = os.path.join(renamed_folder_path, 'index.html')
    if os.path.exists(index_path):
        toc_path = os.path.join(target_root_folder, 'toc.html')
        shutil.copy(index_path, toc_path)
        print(f'Copied and renamed \'index.html\' to \'toc.html\' in {target_root_folder}')

def _get_file_content(file_path, cached_files):
    '''Helper method to get the content of a file, with caching to avoid redundant reads.'''
    if file_path not in cached_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                cached_files[file_path] = file.read()
        except Exception as e:
            print(f'Error reading {file_path}: {e}')
            return None
    return cached_files.get(file_path)

def track_reuse_references(renamed_folder_path, cached_files):
    '''Identify images referenced by HTML files in 'reuse' folder,
       and also check if those files are referenced by any non-reuse folders.'''
    
    needed_images = set()
    referenced_files = {}
    reuse_images = set()

    reuse_folder_path = os.path.join(renamed_folder_path, 'reuse')

    # Step 1: Track which images are referenced in which reuse files
    if os.path.exists(reuse_folder_path):
        for dirpath, _, filenames in os.walk(reuse_folder_path):
            for filename in filenames:
                if filename.lower().endswith('.html'):
                    file_path = os.path.join(dirpath, filename)
                    content = _get_file_content(file_path, cached_files)  # Use the caching function
                    if content:  # Ensure content was retrieved successfully
                        matches = re.findall(r'src=["\\"]([^"\\"]+\\.(?:png|jpg|jpeg|gif))["\\"]', content)
                        reuse_images.update(matches)
                        referenced_files[filename] = matches

    # Step 2: Check if these reuse files are called by any other folder (and thus keep their images)
    all_referenced = set()

    # Check all other folders excluding reuse
    for folder in ['concept', 'reference', 'task', 'glossentry']:
        folder_path = os.path.join(renamed_folder_path, folder)
        if os.path.exists(folder_path):
            for dirpath, _, filenames in os.walk(folder_path):
                for filename in filenames:
                    if filename.lower().endswith('.html'):
                        file_path = os.path.join(dirpath, filename)
                        content = _get_file_content(file_path, cached_files)  # Use the caching function
                        if content:  # Ensure content was retrieved successfully
                            for reuse_file, images in referenced_files.items():
                                if reuse_file in content:
                                    all_referenced.update(images)

    # Step 3: Identify all necessary images
    needed_images.update(all_referenced)  # Images that are shared between reuse and other folders
    needed_images.update(reuse_images)  # Keep images referenced by any reuse files

    return needed_images

def copy_images(self, renamed_folder_path, target_root_folder):
    '''Copy image files to a graphics folder in the target directory.'''
    graphics_folder = os.path.join(target_root_folder, "graphics")
    os.makedirs(graphics_folder, exist_ok=True)
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif')

    # Handle 'graphic' folder
    folder_path = os.path.join(renamed_folder_path, 'graphic')
    if os.path.exists(folder_path):
        for dirpath, _, filenames in os.walk(folder_path):
            for filename in filenames:
                if filename.lower().endswith(image_extensions):
                    # Copy all images by default
                    src_image_path = os.path.join(dirpath, filename)
                    dst_image_path = os.path.join(graphics_folder, filename)
                    
                    # Copy the image to the target graphics folder
                    shutil.copy(src_image_path, dst_image_path)
                    print(f"Copied image '{filename}' to '{graphics_folder}'.")

                    # Here, you could implement additional logic to track or manage which images need to be removed based on your criteria

def remove_unnecessary_images(target_root_folder, needed_images):
    '''Remove unnecessary image files from the target graphics folder.'''
    graphics_folder = os.path.join(target_root_folder, 'graphics')
    if not os.path.exists(graphics_folder):
        return

    for img_name in os.listdir(graphics_folder):
        if img_name not in needed_images:
            img_path = os.path.join(graphics_folder, img_name)
            os.remove(img_path)
            print(f"Removed unnecessary image {img_name} from target graphics folder.")
