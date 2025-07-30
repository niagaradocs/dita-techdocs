"""
 OLD VERSION BACKUP
This script processes DITA-OT HTML5 output to prepare files for a custom help system by:
1. Copying and renaming HTML files based on topic IDs, moving images to a 'graphics' folder, and renaming the legal page as 'index.html'.
2. Renaming the original 'index.html' to 'toc.html' and updating all internal links to match the new file structure.
3. Converting 'toc.html' into an XML file ('toc.xml') formatted according to the help system's requirements by parsing its unordered list structure.
"""
import os
import shutil
import re
from bs4 import BeautifulSoup


# Define the source root folder
source_root_folder = "C:\\dita-ot-dev"


def restructure_files(source_root_folder, doc_folder_name):
    """ Restructure and rename files based on topic IDs and prepare for help system. """
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

                # Handle the renaming of 'WH_LegalNotices_Tridium_N4_0000009932.html' to 'index.html'
                if filename == 'WH_LegalNotices_Tridium_N4_0000009932.html':
                    new_file_name = "index.html"  # Rename the legal notice page to index.html
                    new_file_path = os.path.join(target_root_folder, new_file_name)
                    shutil.copy(html_file_path, new_file_path)
                    print(f"Copied and renamed {filename} to {new_file_name}")
                    file_name_mapping[filename] = new_file_name  # Add to the mapping
                    continue  # Skip further processing for this file

                # Rename the original 'index.html' to 'toc.html'
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

    # After restructuring files, convert toc.html to toc.xml using the provided transformation
    transform_toc_html_to_xml(target_root_folder)


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

def transform_toc_html_to_xml(target_root_folder):
    """Convert toc.html to a formatted toc.xml using the provided structure, and then delete toc.html."""
    toc_html_path = os.path.join(target_root_folder, 'toc.html')
    toc_xml_path = os.path.join(target_root_folder, 'toc.xml')

    if not os.path.exists(toc_html_path):
        print("toc.html not found for conversion.")
        return

    try:
        with open(toc_html_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        toc_content = '<?xml version="1.0" encoding="UTF-8"?>\n<toc>\n'
        toc_content += parse_ul(soup.find('ul'), '')  # Start parsing from the first <ul>
        toc_content += '</toc>'

        with open(toc_xml_path, 'w', encoding='utf-8') as file:
            file.write(toc_content)
        print(f"toc.xml created successfully.")

        # Delete toc.html after conversion
        os.remove(toc_html_path)
        print("toc.html has been deleted after conversion.")

    except Exception as e:
        print(f"An error occurred during toc.xml creation: {e}")


def parse_ul(ul, indent):
    """Parse the <ul> elements to create the corresponding toc.xml structure."""
    items_xml = ''
    for li in ul.find_all('li', recursive=False):
        a = li.find('a')
        if a:
            href = a.get('href')
            text = a.get_text(strip=True)
            items_xml += f'{indent}<tocitem target="{href}" text="{text}">\n'
            child_ul = li.find('ul')
            if child_ul:
                items_xml += parse_ul(child_ul, indent + '   ')
            items_xml += f'{indent}</tocitem>\n'
    return items_xml


# Get document folder name from the user
doc_folder_name = input("Enter the name of the document folder: ")
restructure_files(source_root_folder, doc_folder_name)
