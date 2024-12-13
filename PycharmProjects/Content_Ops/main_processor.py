import os
import zipfile
from bs4 import BeautifulSoup
from file_utils import (
    find_and_unzip_files,
    copy_and_rename_index,
    copy_images,
    flatten_and_process_files,
    clean_target_directory,
    rename_legal_page,
)
from html_utils import transform_toc_html_to_xml


class HelpSystemProcessor:
    def __init__(self, source_root, target_root, doc_list, option):
        self.source_root = source_root
        self.target_root = target_root
        self.doc_list = doc_list
        self.option = option
        self.file_name_mapping = {}

    def process_documents(self):
        """Main entry point to process each document in the list."""
        for doc_folder_name in self.doc_list:
            print(f"Processing document folder: {doc_folder_name}")
            target_root_folder = self._get_target_root_folder(doc_folder_name)

            # Ensure the target directory is cleaned for Option 2
            if self.option == "2":
                clean_target_directory(target_root_folder)

            self.restructure_files(doc_folder_name, target_root_folder)

    def _get_target_root_folder(self, doc_folder_name):
        """Determine target root folder based on the selected option."""
        if self.option == "2":
            # Use the dynamically constructed path from the configuration
            return self.target_root.format(doc_folder_name=doc_folder_name)
        else:
            return os.path.join(self.target_root, doc_folder_name)

    def restructure_files(self, doc_folder_name, target_root_folder):
        """Restructure and rename files based on topic IDs and prepare them for the help system."""
        # Unzip and find the HTML5 folder
        renamed_folder_path = find_and_unzip_files(self.source_root, doc_folder_name)
        html5_folder_path = os.path.join(renamed_folder_path, "ot-output", "html5")
        if not os.path.exists(html5_folder_path):
            print(f"Error: Expected 'html5' folder not found at {html5_folder_path}.")
            return

        # Flatten and process HTML files
        flatten_and_process_files(html5_folder_path, target_root_folder, self.file_name_mapping)

        # Copy and rename index.html to toc.html
        copy_and_rename_index(html5_folder_path, target_root_folder)

        # rename the legal page to index after using original index for toc.html
        rename_legal_page(target_root_folder, self.file_name_mapping)

        # Copy images to the graphics folder
        copy_images(html5_folder_path, target_root_folder)

        # Transform toc.html to toc.xml
        transform_toc_html_to_xml(
            os.path.join(target_root_folder, "toc.html"),
            os.path.join(target_root_folder, "toc.xml"),
        )


# Entry point to run the script
if __name__ == "__main__":
    from config import source_root, target_root, doc_list, option

    # Prompt user for document processing mode
    use_doc_list = input("Use document list? (y/n): ").strip().lower()
    if use_doc_list == "y":
        documents_to_process = doc_list
    elif use_doc_list == "n":
        doc_folder_name = input("Enter the name of the document folder: ").strip()
        documents_to_process = [doc_folder_name]
    else:
        print("Invalid option selected. Exiting.")
        exit(1)

    processor = HelpSystemProcessor(
        source_root, target_root[option], documents_to_process, option
    )
    processor.process_documents()

