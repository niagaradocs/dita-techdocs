# This script flattens the directory structure of html files published by dita-ot. All html files are moved to
# root directory and all hrefs and xrefs are refactored for html files and images.

import os
import shutil
import re

# Define the source root folder
source_root_folder = "C:\\dita-ot-dev"


def restructure_files(source_root_folder, doc_folder_name):
    # Define the target output folder path
    target_base = "c:\\_target_html"
    target_root_folder = os.path.join(target_base, doc_folder_name)

    # Create the target root folder if it doesn't exist
    if not os.path.exists(target_root_folder):
        os.makedirs(target_root_folder)

    # Create the graphics folder within the target folder
    graphics_folder = os.path.join(target_root_folder, 'graphics')
    os.makedirs(graphics_folder, exist_ok=True)

    # Log file path for duplicates and operations
    log_file_path = os.path.join(target_root_folder, 'log.txt')

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
                html_files.append(os.path.join(dirpath, filename))
                shutil.copy(os.path.join(dirpath, filename), target_root_folder)

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

    # Update href/src/xref in copied HTML files
    for html_file in html_files:
        target_file_path = os.path.join(target_root_folder, os.path.basename(html_file))

        try:
            with open(target_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except UnicodeDecodeError:
            print(f"Error reading file {target_file_path}. Skipping.")
            continue  # Skip to the next HTML file

        # Replace 'graphic' folder references with 'graphics' and update links
        content = re.sub(r'((href|src)=["\'])([^"\']+)(["\'])',
                         lambda m: f'{m.group(1)}{update_links(m.group(3), target_root_folder)}{m.group(4)}',
                         content)

        with open(target_file_path, 'w', encoding='utf-8') as file:
            file.write(content)


def update_links(link, target_root_folder):
    """Updates the links to reflect the new structure."""
    # If the link points to an image, place it in the 'graphics' folder
    if link.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        return f'graphics/{os.path.basename(link)}'

    # If the link points to an HTML file, keep it in the root folder
    elif link.lower().endswith('.html'):
        return f'{os.path.basename(link)}'

    # For other cases, return the original link (handle as necessary)
    return link


# Get document folder name from the user
doc_folder_name = input("Enter the name of the document folder: ")
restructure_files(source_root_folder, doc_folder_name)
