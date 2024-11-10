"""
 OLD VERSION ONLY COPIES TO C:\_TARGET_HTML FOLDER
This script processes DITA-OT HTML5 output to prepare files for a custom help system (WB Help) by:
1. Finding and unzipping specific zip files from a subfolder ('source_root_folder).
2. Renaming and restructuring files based on topic IDs, moving images to a 'graphics' folder, and renaming the legal page as 'index.html'.
3. Renaming the original 'index.html' to 'toc.html' and updating all internal links to match the new file structure.
4. Converting 'toc.html' into an XML file ('toc.xml') formatted according to the help system's requirements by parsing its unordered list structure.
"""

import os
import shutil
import re
import zipfile
from bs4 import BeautifulSoup

# Define the source root folder
source_root_folder = "C:\\Users\\e333758\\Honeywell\\PUBLIC Tridium Tech Docs - Workbench_Help - Documents\\_zipfiles"


def find_and_unzip_files(source_root_folder, doc_folder_name):
    """Find zip files matching doc_folder_name and unzip only html5 contents into its own folder."""
    zip_files = [f for f in os.listdir(source_root_folder) if f.endswith('.zip') and f.startswith(doc_folder_name)]

    if not zip_files:
        print(f"No zip files found in {source_root_folder} with the prefix '{doc_folder_name}'.")
        return None
    else:
        print(f"Zip file found in {source_root_folder} with the prefix '{doc_folder_name}'.")

    doc_folder_path = os.path.join(source_root_folder, doc_folder_name)
    os.makedirs(doc_folder_path, exist_ok=True)

    for zip_file in zip_files:
        zip_file_path = os.path.join(source_root_folder, zip_file)

        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                if member.startswith('ot-output/html5/'):
                    target_path = os.path.join(doc_folder_path, member.replace('ot-output/html5/', '', 1))
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with zip_ref.open(member) as source, open(target_path, "wb") as target:
                        shutil.copyfileobj(source, target)

            print(f"Extracted contents of 'html5' from {zip_file} to {doc_folder_path}.")

    return doc_folder_path


def restructure_files(source_root_folder, doc_folder_name):
    """Restructure and rename files based on topic IDs and prepare them for the help system."""
    target_base = "c:\\_target_html"
    target_root_folder = os.path.join(target_base, doc_folder_name)

    if os.path.exists(target_root_folder):
        shutil.rmtree(target_root_folder)
        print(f"Deleted existing folder: {target_root_folder}")

    os.makedirs(target_root_folder, exist_ok=True)

    # Create the graphics folder within the target folder
    graphics_folder = os.path.join(target_root_folder, 'graphics')
    os.makedirs(graphics_folder, exist_ok=True)

    log_file_path = os.path.join(target_root_folder, 'log.txt')
    file_name_mapping = {}

    html_files = []
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif')
    image_count = {}

    renamed_folder_path = find_and_unzip_files(source_root_folder, doc_folder_name)

    if not renamed_folder_path:
        print("No files to process.")
        return

    # Traverse the original directory structure
    for dirpath, dirnames, filenames in os.walk(renamed_folder_path):
        for filename in filenames:
            # Copy only index.html file
            if filename == 'index.html':
                html_file_path = os.path.join(dirpath, filename)
                new_file_path = os.path.join(target_root_folder, filename)
                shutil.copy(html_file_path, new_file_path)
                print(f"Copied {filename} to {target_root_folder}")

                # Rename index.html to toc.html
                toc_file_path = os.path.join(target_root_folder, 'toc.html')
                os.rename(new_file_path, toc_file_path)
                print(f"Renamed {filename} to toc.html")

                # Update internal links in toc.html
                with open(toc_file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                updated_content = re.sub(r'((href|src)=["\'])([^"\']+)(["\'])',
                                         lambda
                                             m: f'{m.group(1)}{update_links(m.group(3), target_root_folder, file_name_mapping)}{m.group(4)}',
                                         content)

                with open(toc_file_path, 'w', encoding='utf-8') as file:
                    file.write(updated_content)
                print("Updated internal links in toc.html.")
                continue

            # Rename the legal notice page to index.html
            if filename == 'WH_LegalNotices_Tridium_N4_0000009932.html':
                new_file_name = "index.html"
                new_file_path = os.path.join(target_root_folder, new_file_name)
                shutil.copy(os.path.join(dirpath, filename), new_file_path)
                print(f"Copied and renamed {filename} to {new_file_name}")
                file_name_mapping[filename] = new_file_name
                continue

            # Handle other HTML files
            if filename.endswith('.html'):
                html_file_path = os.path.join(dirpath, filename)
                new_filename = rename_html_file_based_on_topic_id(html_file_path, target_root_folder, filename)
                if new_filename:
                    file_name_mapping[filename] = new_filename
                    html_files.append(new_filename)
                else:
                    shutil.copy(html_file_path, target_root_folder)

            # Handle image files
            if filename.lower().endswith(image_extensions):
                base_filename, file_extension = os.path.splitext(filename)
                counter = image_count.get(base_filename, 0)

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

    # Convert toc.html to toc.xml
    transform_toc_html_to_xml(target_root_folder)


def rename_html_file_based_on_topic_id(html_file_path, target_root_folder, original_filename):
    """Renames the HTML file based on its topic ID extracted from the <body> or <html> tag."""
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
    except Exception as e:
        print(f"Error reading {html_file_path}: {e}")
        return None

    topic_id = soup.body.get('id', None) or soup.html.get('id', None)

    if topic_id:
        new_file_name = f"{topic_id}.html"
        new_file_path = os.path.join(target_root_folder, new_file_name)
        shutil.copy(html_file_path, new_file_path)
        return new_file_name
    return None


def update_links(link, target_root_folder, file_name_mapping):
    """Updates the links to reflect the new structure."""
    if link.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        return f'graphics/{os.path.basename(link)}'
    elif link.lower().endswith('.html'):
        base_name = os.path.basename(link)
        if base_name in file_name_mapping:
            return f'{file_name_mapping[base_name]}'
        return f'{base_name}'
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
        toc_content += parse_ul(soup.find('ul'), '')
        toc_content += '</toc>'

        with open(toc_xml_path, 'w', encoding='utf-8') as file:
            file.write(toc_content)
        print(f"toc.xml created successfully.")

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