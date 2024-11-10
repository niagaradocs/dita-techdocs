"""
 CURRENT VERSION 1.0, 10/24/2024
This script processes DITA-OT HTML5 output to prepare files for a custom help system by:
1. Finding appropriate zip file(s) and unzipping to target folder for processing.
2. Copying and renaming HTML files based on topic IDs, moving images to a 'graphics' folder, and renaming the legal page as 'index.html'.
3. Renaming the original 'index.html' to 'toc.html' and updating all internal links to match the new file structure.
4. Converting 'toc.html' into an XML file ('toc.xml') formatted according to the help system's requirements by parsing its unordered list structure.
5. Provides options for:
    a. using single input document name or a list that you cn type in "doc_list" below.
    b. target folder: c:\_target_html or c:\niagara\techdocsdev
"""

import os
import shutil
import re
import zipfile
from bs4 import BeautifulSoup

# Define the source root folder
source_root_folder = "C:\\Users\\e333758\\Honeywell\\PUBLIC Tridium Tech Docs - Workbench_Help - Documents\\_zipfiles"

# Predefined document list
doc_list = ['docAlarms']


def ask_for_document_name():
    """Ask the user for a document folder name or use the predefined list."""
    use_doc_list = input("Use document list? (y/n): ").strip().lower()

    if use_doc_list == 'y':
        return doc_list  # Returning the predefined document list
    elif use_doc_list == 'n':
        doc_folder_name = input("Enter the name of the document folder: ")
        return [doc_folder_name]  # Returning a list with the single folder name
    else:
        print("Invalid option selected. Exiting.")
        exit(1)


def select_output_folder():
    print("Select an output folder option:")
    print("1: '_target_html' folder")
    print("2: 'techdocsdev' folder")

    option = input("Enter the option number (1 or 2): ")

    if option == "1":
        target_base = "c:\\_target_html"
    elif option == "2":
        target_base = "C:\\niagara\\techdocsdev\\docs"
    else:
        print("Invalid option selected.")
        exit(1)

    return target_base, option


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


def restructure_files(source_root_folder, doc_folder_name, target_root_folder):
    global file_name_mapping  # Declare this if it's not already global
    file_name_mapping = {}  # Ensure it's initialized before use
    """Restructure and rename files based on topic IDs and prepare them for the help system."""
    # Create the graphics folder within the target folder
    graphics_folder = os.path.join(target_root_folder, 'graphics')
    os.makedirs(graphics_folder, exist_ok=True)

    log_file_path = os.path.join(target_root_folder, 'log.txt')

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

                # Example of logging the file_name_mapping
                print("Current file name mapping:")
                for original, new in file_name_mapping.items():
                    print(f"{original} -> {new}")

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
    print(f"Attempting to update link: {link}")  # Display the link being processed
    if link.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        updated_link = f'graphics/{os.path.basename(link)}'
    elif link.lower().endswith('.html'):
        base_name = os.path.basename(link)
        if base_name in file_name_mapping:
            updated_link = f'{file_name_mapping[base_name]}'
            print(f"Updated link from {base_name} to {updated_link}")  # Confirm successful update
        else:
            updated_link = base_name
            print(f"No mapping found for: {base_name}")  # Log missing mapping
    else:
        updated_link = link
    return updated_link



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


# Starting the script by asking about the document name
doc_list = ask_for_document_name()

# Select output folder option before processing documents
target_base, option = select_output_folder()

# Process each document in the list using its unique target folder
for doc_folder_name in doc_list:
    print(f"Processing document folder: {doc_folder_name}")
    if option == "2":
        # For option 2, create a unique path for each document
        target_root_folder = os.path.join(target_base, doc_folder_name, f"{doc_folder_name}-doc", "src", "doc")
    else:
        # For option 1, create a unique path as well
        target_root_folder = os.path.join(target_base, doc_folder_name)

    restructure_files(source_root_folder, doc_folder_name, target_root_folder)