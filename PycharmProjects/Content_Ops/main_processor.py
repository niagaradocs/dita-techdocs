import os
import shutil
import re
import zipfile
from bs4 import BeautifulSoup
from file_utils import find_and_unzip_files, copy_and_rename_index, track_reuse_references, copy_images, remove_unnecessary_images  # Importing from file_utils
from html_utils import transform_toc_html_to_xml, format_html  # Assuming you have other utilities in html_utils

class HelpSystemProcessor:
    def __init__(self, source_root, target_base, doc_list, option):
        self.source_root = source_root
        self.target_base = target_base
        self.doc_list = doc_list
        self.option = option
        self.file_name_mapping = {}
        self.image_count = {}
        self.cached_files = {}  # Cache to store HTML file content for efficiency

    def process_documents(self):
        '''Main entry point to process each document in the list.'''
        for doc_folder_name in self.doc_list:
            print(f'Processing document folder: {doc_folder_name}')
            target_root_folder = self._get_target_root_folder(doc_folder_name)
            self.restructure_files(doc_folder_name, target_root_folder)

    def _get_target_root_folder(self, doc_folder_name):
        '''Determine target root folder based on the selected option.'''
        if self.option == '2':
            return os.path.join(self.target_base, doc_folder_name, f'{doc_folder_name}-doc', 'src', 'doc')
        else:
            return os.path.join(self.target_base, doc_folder_name)

    def restructure_files(self, doc_folder_name, target_root_folder):
        '''Restructure and rename files based on topic IDs and prepare them for the help system.'''
        # Step 1: Unzip files
        renamed_folder_path = find_and_unzip_files(self.source_root, doc_folder_name)
        if not renamed_folder_path:
            print('No files to process.')
            return

        # Step 2: Copy and rename index.html to toc.html
        copy_and_rename_index(renamed_folder_path, target_root_folder)

        # Step 3: Track required images based on reuse references
        needed_images = track_reuse_references(target_root_folder, renamed_folder_path, self.cached_files)

        # Step 4: Copy images from 'graphics' folder to the target 'graphics' folder
        copy_images(renamed_folder_path, target_root_folder, needed_images)

        # Step 5: Remove unnecessary images from the graphics folder
        remove_unnecessary_images(target_root_folder, needed_images)

        # Assuming the rest of the functions for renaming HTML files, updating links, formatting, etc., are defined elsewhere
        self.rename_html_files(renamed_folder_path, target_root_folder)
        self.update_links_in_html(target_root_folder)
        self.format_html_files(target_root_folder)

        # Step 9: Convert toc.html to toc.xml
        transform_toc_html_to_xml(os.path.join(target_root_folder, 'toc.html'), os.path.join(target_root_folder, 'toc.xml'))

    def rename_html_files(self, renamed_folder_path, target_root_folder):
        '''Rename HTML files based on topic IDs.'''
        for dirpath, _, filenames in os.walk(renamed_folder_path):
            for filename in filenames:
                if filename.endswith('.html') and filename not in ['index.html', 'WH_LegalNotices_Tridium_N4_0000009932.html']:
                    html_file_path = os.path.join(dirpath, filename)
                    new_filename = self.rename_html_file_based_on_topic_id(html_file_path, target_root_folder, filename)
                    if new_filename:
                        self.file_name_mapping[filename] = new_filename

    def rename_html_file_based_on_topic_id(self, html_file_path, target_root_folder, original_filename):
        '''Renames the HTML file based on its topic ID extracted from the <body> or <html> tag.'''
        content = self._get_file_content(html_file_path) 
        if not content:
            return None

        try:
            soup = BeautifulSoup(content, 'html.parser')
        except Exception as e:
            print(f'Error parsing HTML for {html_file_path}: {e}')
            return None

        topic_id = soup.body.get('id', None) or soup.html.get('id', None)

        if topic_id:
            new_file_name = f'{topic_id}.html'
            new_file_path = os.path.join(target_root_folder, new_file_name)
            shutil.copy(html_file_path, new_file_path)
            print(f'Renamed HTML file {original_filename} to {new_file_name}')
            return new_file_name
        return None

    def update_links_in_html(self, target_root_folder):
        '''Update links in HTML files to match the new file structure.'''
    for dirpath, _, filenames in os.walk(target_root_folder):
        for filename in filenames:
            if filename.endswith('.html'):
                file_path = os.path.join(dirpath, filename)
                content = self._get_file_content(file_path)
                if content:
                    updated_content = re.sub(
                        r'(?P<attr>(href|src)=[\\''])(?P<url>.*?)([\\''])',
                        lambda m: f"{m.group('attr')}{self.update_links(m.group('url'))}{m.group(4)}",
                        content
                    )

                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(updated_content)
                    print(f'Updated internal links in {filename}.')

    def format_html_files(self, target_root_folder):
        '''Ensure <head>, </head>, <title>, </title>, <body>, and </body> tags are on separate lines in all HTML files.'''
        for dirpath, _, filenames in os.walk(target_root_folder):
            for filename in filenames:
                if filename.endswith('.html'):
                    file_path = os.path.join(dirpath, filename)
                    content = self._get_file_content(file_path)
                    if content:
                        # Ensure specified tags are on separate lines
                        content = re.sub(r'(\\\\s*<head>)', r'\\\\n\\\\1\\\\n', content)
                        content = re.sub(r'(</head>)', r'\\\\n\\\\1\\\\n', content)
                        content = re.sub(r'(\\\\s*<title>)', r'\\\\n\\\\1\\\\n', content)
                        content = re.sub(r'(</title>)', r'\\\\n\\\\1\\\\n', content)
                        content = re.sub(r'(\\\\s*<body[^>]*>)', r'\\\\n\\\\1\\\\n', content)
                        content = re.sub(r'(</body>)', r'\\\\n\\\\1\\\\n', content)

                        with open(file_path, 'w', encoding='utf-8') as file:
                            file.write(content)
                        print(f'Formatted {filename} to have specific tags on separate lines.')

    def _get_file_content(self, file_path):
        '''Helper method to get the content of a file, with caching to avoid redundant reads.'''
        if file_path not in self.cached_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.cached_files[file_path] = file.read()
            except Exception as e:
                print(f'Error reading {file_path}: {e}')
                return None
        return self.cached_files.get(file_path)

    def update_links(self, link):
        '''Update a link based on the file name mapping.'''
        if link.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            return f'graphics/{os.path.basename(link)}'
        elif link.lower().endswith('.html'):
            base_name = os.path.basename(link)
            return self.file_name_mapping.get(base_name, base_name)
        else:
            return link

# Entry point to run the script
if __name__ == '__main__':
    source_root_folder = 'C:\\\\\\\\Users\\\\\\\\e333758\\\\\\\\Honeywell\\\\\\\\PUBLIC Tridium Tech Docs - Workbench_Help - Documents\\\\\\\\_zipfiles'
    doc_list = ['docAlarms']

    # Ask for document name and output folder
    use_doc_list = input('Use document list? (y/n): ').strip().lower()
    if use_doc_list == 'y':
        doc_list = doc_list
    elif use_doc_list == 'n':
        doc_folder_name = input('Enter the name of the document folder: ')
        doc_list = [doc_folder_name]
    else:
        print('Invalid option selected. Exiting.')
        exit(1)

    print('Select an output folder option:')
    print('1: _target_html folder')
    print('2: techdocsdev folder')
    option = input('Enter the option number (1 or 2): ')
    target_base = 'c:\\\\\\\\_target_html' if option == '1' else 'C:\\\\\\\\niagara\\\\\\\\techdocsdev\\\\\\\\docs'

    processor = HelpSystemProcessor(source_root_folder, target_base, doc_list, option)
    processor.process_documents()