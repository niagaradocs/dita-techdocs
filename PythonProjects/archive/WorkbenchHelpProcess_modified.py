"""
CURRENT VERSION 1.1 Active, 14/01/2025

This script processes DITA-OT HTML5 output to prepare files for a custom help system by:

1. Asking user for options: Use a pre-defined list or enter a single document name.
    a. User can select between two target folders: c:\_target_html or c:\niagara\techdocsdev.
2. Locating appropriate zip file(s) and extracting contents into the target folder for processing.
3. Copying and renaming HTML files based on topic IDs, organizing images into a 'graphics' folder, and renaming the legal page to 'index.html'.
4. Renaming the existing 'index.html' to 'toc.html' and updating all internal links to match the new file structure.
5. Converting 'toc.html' into an XML file ('toc.xml'), adhering to the help system's formatting requirements, while ensuring all list elements are properly nested.
6. Updating the section for handling missing or duplicate image names to avoid overwriting.
7. Ensuring specified HTML tags are formatted on separate lines for clarity and readability.

"""
import os
import shutil
import re
import zipfile
from bs4 import BeautifulSoup


class HelpSystemProcessor:
    def __init__(self, source_root, target_base, doc_list, option):
        self.source_root = source_root
        self.target_base = target_base
        self.doc_list = doc_list
        self.option = option
        self.file_name_mapping = {}
        self.image_count = {}

    def process_documents(self):
        """Main entry point to process each document in the list."""
        for doc_folder_name in self.doc_list:
            print(f"Processing document folder: {doc_folder_name}")
            target_root_folder = self._get_target_root_folder(doc_folder_name)
            self.restructure_files(doc_folder_name, target_root_folder)

    def _get_target_root_folder(self, doc_folder_name):
        """Determine target root folder based on the selected option."""
        if self.option == "2":
            return os.path.join(self.target_base, doc_folder_name, f"{doc_folder_name}-doc", "src", "doc")
        else:
            return os.path.join(self.target_base, doc_folder_name)

    def restructure_files(self, doc_folder_name, target_root_folder):
        """Restructure and rename files based on topic IDs and prepare them for the help system."""
        # Step 1: Unzip files
        renamed_folder_path = self.find_and_unzip_files(doc_folder_name)
        if not renamed_folder_path:
            print("No files to process.")
            return

        # Step 2: Copy and rename index.html to toc.html
        self.copy_and_rename_index(renamed_folder_path, target_root_folder)

        # Step 3: Copy images from 'graphics' folder to the target 'graphics' folder
        self.copy_images(renamed_folder_path, target_root_folder)

        # Step 4: Rename HTML files based on topic IDs and update mapping
        self.rename_html_files(renamed_folder_path, target_root_folder)

        # Step 5: Update links in HTML files
        self.update_links_in_html(target_root_folder)

        # Step 6: Format HTML files to ensure specific tags are on separate lines
        self.format_html_files(target_root_folder)

        # Step 7: Remove unused images
        self.remove_unused_images(target_root_folder)

        # Step 8: Convert toc.html to toc.xml
        self.transform_toc_html_to_xml(target_root_folder)

    def find_and_unzip_files(self, doc_folder_name):
        """Find zip files matching doc_folder_name and unzip only html5 contents into its own folder."""
        zip_files = [f for f in os.listdir(self.source_root) if f.endswith('.zip') and f.startswith(doc_folder_name)]

        if not zip_files:
            print(f"No zip files found in {self.source_root} with the prefix '{doc_folder_name}'.")
            return None

        doc_folder_path = os.path.join(self.source_root, doc_folder_name)
        os.makedirs(doc_folder_path, exist_ok=True)

        for zip_file in zip_files:
            zip_file_path = os.path.join(self.source_root, zip_file)

            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                for member in zip_ref.namelist():
                    if member.startswith('ot-output/html5/'):
                        target_path = os.path.join(doc_folder_path, member.replace('ot-output/html5/', '', 1))
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)

                        # Correctly handle source file stream as binary
                        with zip_ref.open(member) as source:
                            with open(target_path, "wb") as target:
                                # Ensure that the source is read as bytes
                                if isinstance(source, bytes):
                                    target.write(source)
                                else:
                                    shutil.copyfileobj(source, target)

                print(f"Extracted contents of 'html5' from {zip_file} to {doc_folder_path}.")

        return doc_folder_path

    def copy_and_rename_index(self, renamed_folder_path, target_root_folder):
        """Copy and rename index.html to toc.html."""
        index_path = os.path.join(renamed_folder_path, 'index.html')
        if os.path.exists(index_path):
            toc_path = os.path.join(target_root_folder, 'toc.html')
            shutil.copy(index_path, toc_path)
            print(f"Copied and renamed 'index.html' to 'toc.html' in {target_root_folder}")

    def copy_images(self, renamed_folder_path, target_root_folder):
        """Copy image files to a graphics folder in the target directory."""
        graphics_folder = os.path.join(target_root_folder, 'graphics')
        os.makedirs(graphics_folder, exist_ok=True)
        image_extensions = ('.png', '.jpg', '.jpeg', '.gif')

        # Handle 'graphics' folder NOTE SOURCE FOLDER IS 'graphic' NOT 'graphics'
        folder_path = os.path.join(renamed_folder_path, 'graphic')
        if os.path.exists(folder_path):
            for dirpath, _, filenames in os.walk(folder_path):
                for filename in filenames:
                    if filename.lower().endswith(image_extensions):
                        base_filename, file_extension = os.path.splitext(filename)
                        counter = self.image_count.get(base_filename, 0)

                        # Handle duplicate image names
                        while counter > 0:
                            new_filename = f"{base_filename}_{counter}{file_extension}"
                            if new_filename in filenames:
                                counter += 1
                            else:
                                break

                        if counter > 0:
                            filename = f"{base_filename}_{counter}{file_extension}"

                        shutil.copy(os.path.join(dirpath, filename), os.path.join(graphics_folder, filename))
                        self.image_count[base_filename] = counter + 1

    def rename_html_files(self, renamed_folder_path, target_root_folder):
        """Rename HTML files based on topic IDs."""
        for dirpath, _, filenames in os.walk(renamed_folder_path):
            for filename in filenames:
                if filename.endswith('.html'):
                    html_file_path = os.path.join(dirpath, filename)
                    new_filename = self.rename_html_file_based_on_topic_id(html_file_path, target_root_folder, filename)
                    if new_filename:
                        self.file_name_mapping[filename] = new_filename

    def rename_html_file_based_on_topic_id(self, html_file_path, target_root_folder, original_filename):
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

    def update_links_in_html(self, target_root_folder):
        """Update links in HTML files to match the new file structure, including xref elements."""
        for dirpath, _, filenames in os.walk(target_root_folder):
            for filename in filenames:
                if filename.endswith('.html'):
                    file_path = os.path.join(dirpath, filename)
                    with open(file_path, 'r', encoding='utf-8') as file:
                        soup = BeautifulSoup(file, 'html.parser')
                    for tag in soup.find_all(True):
                        for attr in ['href', 'src']:
                            if tag.has_attr(attr):
                                tag[attr] = self.update_links(tag[attr])
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(str(soup))
                    print(f"Updated internal links in {filename}.")


    def update_links(self, link):
        """Update a link based on the file name mapping."""
        if link.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            return f'graphics/{os.path.basename(link)}'
        elif link.lower().endswith('.html'):
            base_name = os.path.basename(link)
            return self.file_name_mapping.get(base_name, base_name)
        else:
            return link

    def format_html_files(self, target_root_folder):
        """Ensure <head>, </head>, <title>, </title>, <body>, and </body> tags are on separate lines in all HTML files."""
        for dirpath, _, filenames in os.walk(target_root_folder):
            for filename in filenames:
                if filename.endswith('.html') or filename == 'toc.html':
                    file_path = os.path.join(dirpath, filename)
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()

                    # Ensure specified tags are on separate lines
                    content = re.sub(r'(\s*<head>)', r'\n\1\n', content)
                    content = re.sub(r'(</head>)', r'\n\1\n', content)
                    content = re.sub(r'(\s*<title>)', r'\n\1\n', content)
                    content = re.sub(r'(</title>)', r'\n\1\n', content)
                    content = re.sub(r'(\s*<body[^>]*>)', r'\n\1\n', content)
                    content = re.sub(r'(</body>)', r'\n\1\n', content)

                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(content)
                    print(f"Formatted {filename} to have specific tags on separate lines.")

    def remove_unused_images(self, target_root_folder):
        """Remove images in the 'graphics' folder that are not referenced in any HTML file."""
    
        graphics_folder = os.path.join(target_root_folder, 'graphics')
        if not os.path.exists(graphics_folder):
            print("Graphics folder does not exist, skipping cleanup.")
            return
        
        # Collect all image references from HTML files
        used_images = set()
        for dirpath, _, filenames in os.walk(target_root_folder):
            for filename in filenames:
                if filename.endswith('.html'):
                    file_path = os.path.join(dirpath, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            soup = BeautifulSoup(file, 'html.parser')
                        
                        # Find all image tags
                        for img in soup.find_all('img'):
                            src = img.get('src')
                            if src:
                                image_name = os.path.basename(src)
                                used_images.add(image_name)
                    
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")

        # Get list of all images in the graphics folder
        all_images = {img for img in os.listdir(graphics_folder) if img.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))}

        # Find unused images
        unused_images = all_images - used_images

        # Remove unused images
        for img in unused_images:
            img_path = os.path.join(graphics_folder, img)
            try:
                os.remove(img_path)
                print(f"Deleted unused image: {img}")
            except Exception as e:
                print(f"Error deleting {img}: {e}")

        print("Unused image cleanup completed.")

    def transform_toc_html_to_xml(self, target_root_folder):
        """Convert toc.html to a formatted toc.xml using the provided structure, and then delete toc.html."""
        toc_html_path = os.path.join(target_root_folder, 'toc.html')
        toc_xml_path = os.path.join(target_root_folder, 'toc.xml')
        legal_page_path = os.path.join(target_root_folder, 'legal_niagara_tridium.html')
        index_path = os.path.join(target_root_folder, 'index.html')

        if not os.path.exists(toc_html_path):
            print("toc.html not found for conversion.")
            return

        try:
            with open(toc_html_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')

            toc_items = self.parse_ul(soup.find('ul'), '')

            # Check if toc_items is empty before processing
            if not toc_items.strip():
                raise ValueError("Error: 'toc.html' generated no items. Cannot proceed.")

            # Prepare the initial XML content
            toc_content = '<?xml version="1.0" encoding="UTF-8"?>\n<toc>\n'

            # Check the first line and make necessary adjustments for the legal item
            lines = toc_items.splitlines()
            first_line = lines[0].strip() if lines else ""

            # Determine the proper format for the Legal Notice tocitem
            if first_line == '<tocitem target="index.html" text="Legal Notice">':
                toc_content += toc_items + '</tocitem>'  # Properly close

            elif first_line == '<tocitem target="legal_niagara_tridium.html" text="Legal Notice">':
                lines[0] = '<tocitem target="index.html" text="Legal Notice">'  # Change opening tag
                toc_content += '\n'.join(lines) + '</tocitem>'  # Properly close

            else:
                if not first_line.startswith('<tocitem '):
                    raise ValueError("Error: Unexpected content found; expected <tocitem> format.")
                toc_content += '<tocitem target="index.html" text="Legal Notice"></tocitem>\n' + toc_items

            # Close the toc element
            toc_content += '</toc>'

            with open(toc_xml_path, 'w', encoding='utf-8') as file:
                file.write(toc_content)
                print("toc.xml created successfully.")

            os.remove(toc_html_path)
            print("toc.html has been deleted after conversion.")

            # Check for existing index.html and delete it if it exists
            if os.path.exists(index_path):
                os.remove(index_path)
                print("Deleted existing index.html before renaming.")

            # Renaming legal_niagara_tridium.html to index.html
            if os.path.exists(legal_page_path):
                os.rename(legal_page_path, index_path)
                print("Renamed legal_niagara_tridium.html to index.html.")
            else:
                print("legal_niagara_tridium.html not found for renaming.")

        except Exception as e:
            print(f"An error occurred during toc.xml creation: {e}")

    def parse_ul(self, ul, indent):
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
                    items_xml += self.parse_ul(child_ul, indent + ' ')
                items_xml += f'{indent}</tocitem>\n'
        return items_xml

# Entry point to run the script
if __name__ == "__main__":
    source_root_folder = "C:\\Users\\e333758\\Honeywell\\PUBLIC Tridium Tech Docs - Workbench_Help - Documents\\_zipfiles"
    doc_list = ['docKitControl','docMqtt','docProvisioning','docRdbms']

    # Ask for document name and output folder
    use_doc_list = input("Use document list? (y/n): ").strip().lower()
    if use_doc_list == 'y':
        doc_list = doc_list
    elif use_doc_list == 'n':
        doc_folder_name = input("Enter the name of the document folder: ")
        doc_list = [doc_folder_name]
    else:
        print("Invalid option selected. Exiting.")
        exit(1)

    print("Select an output folder option:")
    print("1: '_target_html' folder")
    print("2: 'techdocsdev' folder")
    option = input("Enter the option number (1 or 2): ")
    target_base = "c:\\_target_html" if option == "1" else "C:\\niagara\\techdocsdev\\docs"

    processor = HelpSystemProcessor(source_root_folder, target_base, doc_list, option)
    processor.process_documents()
