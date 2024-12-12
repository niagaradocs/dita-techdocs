import os
import shutil
import zipfile
from bs4 import BeautifulSoup


def find_and_unzip_files(source_root, doc_folder_name):
    """
    Finds zip files matching the document folder name and extracts only
    the HTML5 content into a corresponding folder.
    """
    zip_files = [f for f in os.listdir(source_root) if f.endswith(".zip") and f.startswith(doc_folder_name)]
    if not zip_files:
        print(f"No zip files found in {source_root} with the prefix '{doc_folder_name}'.")
        return None

    doc_folder_path = os.path.join(source_root, doc_folder_name)
    os.makedirs(doc_folder_path, exist_ok=True)

    for zip_file in zip_files:
        zip_file_path = os.path.join(source_root, zip_file)
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(doc_folder_path)
        print(f"Extracted contents from {zip_file} to {doc_folder_path}.")
    return doc_folder_path


def flatten_and_process_files(source_folder, target_folder, file_name_mapping):
    """
    Flattens the folder structure by moving HTML files to the root target folder
    and graphic files to the 'graphics' subfolder in the target directory.
    Updates references in the HTML files to reflect the new structure.
    """
    os.makedirs(target_folder, exist_ok=True)
    graphics_folder = os.path.join(target_folder, 'graphics')
    os.makedirs(graphics_folder, exist_ok=True)

    for root, _, files in os.walk(source_folder):
        for file in files:
            source_file_path = os.path.join(root, file)

            if file.endswith('.html'):
                # Flatten HTML files
                flatten_html_file(source_file_path, target_folder, file_name_mapping)
            elif file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
                # Move graphic files to the 'graphics' folder
                target_graphic_path = os.path.join(graphics_folder, file)
                shutil.copy(source_file_path, target_graphic_path)
                print(f"Copied graphic: {source_file_path} -> {target_graphic_path}")

    # Update references in all flattened HTML files
    update_references_in_flattened_files(target_folder, file_name_mapping)


def flatten_html_file(source_file_path, target_folder, file_name_mapping):
    """
    Copies an HTML file to the target folder and updates the file name if necessary.
    """
    try:
        with open(source_file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        # Extract topic ID from <body> or <html> tag
        topic_id = soup.body.get('id', None) or soup.html.get('id', None)
        new_file_name = f"{topic_id}.html" if topic_id else os.path.basename(source_file_path)
        target_file_path = os.path.join(target_folder, new_file_name)

        # Save the flattened file
        with open(target_file_path, 'w', encoding='utf-8') as file:
            file.write(str(soup))
        print(f"Flattened and moved HTML: {source_file_path} -> {target_file_path}")

        # Update the mapping for reference updates
        file_name_mapping[os.path.basename(source_file_path)] = new_file_name
    except Exception as e:
        print(f"Error processing HTML file {source_file_path}: {e}")


def update_references_in_flattened_files(target_folder, file_name_mapping):
    """
    Updates `href` and `src` attributes in the HTML files in the target folder
    to reflect the flattened structure for HTML and graphics.
    """
    graphics_folder = 'graphics/'  # Relative path to the graphics folder

    for root, _, files in os.walk(target_folder):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        soup = BeautifulSoup(f, 'html.parser')

                    # Update all `href` and `src` attributes
                    for tag in soup.find_all(['a', 'img', 'script', 'link']):
                        attr = 'href' if tag.name in ['a', 'link'] else 'src'
                        if attr in tag.attrs:
                            original_ref = tag[attr]
                            tag[attr] = update_reference(original_ref, file_name_mapping, graphics_folder)

                    # Write the updated HTML back to the file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(str(soup))
                    print(f"Updated references in: {file_path}")
                except Exception as e:
                    print(f"Error updating references in {file_path}: {e}")


def update_reference(reference, file_name_mapping, graphics_folder):
    """
    Updates a single reference based on the file name mapping for flattened structure.
    """
    if reference.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
        # For graphic files, redirect to the 'graphics' folder
        return f"{graphics_folder}{os.path.basename(reference)}"
    elif reference.lower().endswith('.html'):
        # For HTML files, use the file name mapping
        base_name = os.path.basename(reference)
        return file_name_mapping.get(base_name, base_name)
    else:
        # For other references, return as-is
        return reference


def clean_target_directory(target_folder):
    """
    Deletes all files and folders in the target folder.
    """
    if os.path.exists(target_folder):
        for item in os.listdir(target_folder):
            item_path = os.path.join(target_folder, item)
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        print(f"Cleaned target directory: {target_folder}")


def copy_and_rename_index(html5_folder_path, target_root_folder):
    """
    Copy and rename index.html to toc.html.
    """
    index_path = os.path.join(html5_folder_path, "index.html")
    toc_path = os.path.join(target_root_folder, "toc.html")

    if not os.path.exists(index_path):
        print(f"Error: 'index.html' not found in {html5_folder_path}.")
        return

    shutil.copy(index_path, toc_path)
    print(f"Copied and renamed 'index.html' to 'toc.html' in {target_root_folder}.")


def copy_images(html5_folder_path, target_root_folder):
    """
    Copy all images from 'graphic' to 'graphics'.
    """
    graphic_folder = os.path.join(html5_folder_path, "graphic")
    graphics_folder = os.path.join(target_root_folder, "graphics")
    os.makedirs(graphics_folder, exist_ok=True)

    if os.path.exists(graphic_folder):
        for img_file in os.listdir(graphic_folder):
            src_img_path = os.path.join(graphic_folder, img_file)
            tgt_img_path = os.path.join(graphics_folder, img_file)
            shutil.copy(src_img_path, tgt_img_path)
            print(f"Copied {img_file} to graphics folder.")
