# This script flattens the directory structure of html files published by dita-ot. All html files are moved to
# root directory and all hrefs and xrefs are refactored for html files and images. Also, all file are renamed to match
# xml topic ID values which should be loaded in the <body> tags of each html topic.

import os
import shutil
import re
from bs4 import BeautifulSoup

# Define the source root folder
source_root_folder = "C:\\dita-ot-dev"

def restructure_files(source_root_folder, doc_folder_name):
    # Define the target output folder path
    target_base = "c:\\_target_html"
    target_root_folder = os.path.join(target_base, doc_folder_name)

    # Delete the existing target folder if it exists to ensure clean copy
    if os.path.exists(target_root_folder):
        shutil.rmtree(target_root_folder)
        print(f"Deleted existing folder: {target_root_folder}")

    # Create the target root folder after deleting the previous one
    os.makedirs(target_root_folder, exist_ok=True)

    # Create the graphics folder within the target folder
    graphics_folder = os.path.join(target_root_folder, 'graphics')
    os.makedirs(graphics_folder, exist_ok=True)

    # Log file path for duplicates and operations
    log_file_path = os.path.join(target_root_folder, 'log.txt')

    # Dictionary to store the mapping between original filenames and new topic ID-based filenames
    file_name_mapping = {}

    # Variables to store the HTML and image files
    html_files = []
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif')
    image_count = {}

    # Traverse the original directory structure
    for dirpath, dirnames, filenames in os.walk(source_root_folder):
        if dirpath == target_root_folder:  # Skip the target structure itself
            continue

        for filename in filenames:
            # Handle HTML files
            if filename.endswith('.html'):
                html_file_path = os.path.join(dirpath, filename)

                # Special handling for 'WH_LegalNotices_Tridium_N4_0000009932.html'
                if filename == 'WH_LegalNotices_Tridium_N4_0000009932.html':
                    new_file_name = "legal_niagara_tridium.html"
                    new_file_path = os.path.join(target_root_folder, new_file_name)
                    shutil.copy(html_file_path, new_file_path)
                    print(f"Copied and renamed {filename} to {new_file_name}")
                    file_name_mapping[filename] = new_file_name  # Add to the mapping
                    continue  # Skip further processing for this file

                # Process index.html -> toc.html renaming
                if filename == 'index.html':
                    new_file_name = "toc.html"  # Rename index.html to toc.html
                    new_file_path = os.path.join(target_root_folder, new_file_name)
                    shutil.copy(html_file_path, new_file_path)
                    html_files.append(new_file_name)  # Ensure we update the links in toc.html
                    print(f"Copied and renamed {filename} to {new_file_name}")
                    continue

                # Rename file based on topic ID
                new_filename = rename_html_file_based_on_topic_id(html_file_path, target_root_folder, filename)
                if new_filename:
                    file_name_mapping[filename] = new_filename  # Add old and new name to the mapping
                    html_files.append(new_filename)
                else:
                    shutil.copy(html_file_path, target_root_folder)

            # Handle image files
            if filename.lower().endswith(image_extensions):
                base_filename, file_extension = os.path.splitext(filename)
                counter = image_count.get(base_filename, 0)

                # Ensure unique filenames for duplicates
                while counter > 0:
                    new_filename = f"{base_filename}_{counter}{file_extension}"
                    if new_filename in filenames:
                        counter += 1
                    else:
                        break

                if counter > 0:
                    log_message = f"[WARNING] Duplicate file found: {filename}. Renamed to {new_filename}\n"
                    with open(log_file_path, 'a') as log_file:
                        log_file.write(log_message)
                    filename = new_filename

                shutil.copy(os.path.join(dirpath, filename), os.path.join(graphics_folder, filename))
                image_count[base_filename] = counter + 1

    # Update href/src/xref in copied HTML files and toc.html
    for html_file in html_files:
        target_file_path = os.path.join(target_root_folder, os.path.basename(html_file))

        try:
            with open(target_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except UnicodeDecodeError:
            print(f"Error reading file {target_file_path}. Skipping.")
            continue  # Skip to the next HTML file

        # Replace 'graphic' folder references with 'graphics' and update links using the mapping
        content = re.sub(r'((href|src)=["\'])([^"\']+)(["\'])',
                         lambda m: f'{m.group(1)}{update_links(m.group(3), target_root_folder, file_name_mapping)}{m.group(4)}',
                         content)

        with open(target_file_path, 'w', encoding='utf-8') as file:
            file.write(content)


def rename_html_file_based_on_topic_id(html_file_path, target_root_folder, original_filename):
    """Renames the HTML file based on its topic ID extracted from the <body> or <html> tag."""
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
    except Exception as e:
        print(f"Error reading {html_file_path}: {e}")
        return None

    # Extract the topic ID (assuming it's stored in the <body> or <html> tag)
    topic_id = soup.body.get('id', None) or soup.html.get('id', None)

    if topic_id:
        new_file_name = f"{topic_id}.html"
        new_file_path = os.path.join(target_root_folder, new_file_name)
        shutil.copy(html_file_path, new_file_path)  # Use copy instead of move
        return new_file_name
    return None


def update_links(link, target_root_folder, file_name_mapping):
    """Updates the links to reflect the new structure."""
    # If the link points to an image, place it in the 'graphics' folder
    if link.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        return f'graphics/{os.path.basename(link)}'

    # If the link points to an HTML file, check the mapping and update the link
    elif link.lower().endswith('.html'):
        base_name = os.path.basename(link)
        if base_name in file_name_mapping:
            return f'{file_name_mapping[base_name]}'  # Update to the new filename based on the topic ID
        return f'{base_name}'  # Keep it the same if not in the mapping

    # For other cases, return the original link (handle as necessary)
    return link


# Get document folder name from the user
doc_folder_name = input("Enter the name of the document folder: ")
restructure_files(source_root_folder, doc_folder_name)
