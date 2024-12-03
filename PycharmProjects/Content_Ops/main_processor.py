import os
import shutil
import re
import zipfile
from bs4 import BeautifulSoup
from file_utils import find_and_unzip_files, copy_and_rename_index  # Importing from file_utils module
from html_utils import transform_toc_html_to_xml  # Importing from html_utils module

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
        renamed_folder_path = find_and_unzip_files(self.source_root, doc_folder_name)
        if not renamed_folder_path:
            print("No files to process.")
            return

        # Step 2: Copy and rename index.html to toc.html
        copy_and_rename_index(renamed_folder_path, target_root_folder)

        # Step 3: Convert toc.html to toc.xml
        transform_toc_html_to_xml(
            os.path.join(target_root_folder, 'toc.html'),
            os.path.join(target_root_folder, 'toc.xml')
        )

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
                    items_xml += self.parse_ul(child_ul, indent + '   ')
                items_xml += f'{indent}</tocitem>\n'
        return items_xml

# Entry point to run the script
if __name__ == "__main__":
    source_root_folder = "C:\\Users\\e333758\\Honeywell\\PUBLIC Tridium Tech Docs - Workbench_Help - Documents\\_zipfiles"
    doc_list = ['docAlarms']

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
