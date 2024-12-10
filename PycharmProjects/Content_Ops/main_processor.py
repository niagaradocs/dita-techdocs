import os
import logging
from config import SOURCE_ROOT, TARGET_ROOT, DOC_LIST, LOGGING_LEVEL
from file_utils import find_and_unzip_files, copy_and_rename_index, copy_images
from html_utils import transform_toc_html_to_xml, format_html

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
            logging.info(f"Processing document folder: {doc_folder_name}")
            target_root_folder = self._get_target_root_folder(doc_folder_name)
            self.restructure_files(doc_folder_name, target_root_folder)

    def _get_target_root_folder(self, doc_folder_name):
        """Determine target root folder based on the selected option."""
        return os.path.join(self.target_root[self.option], doc_folder_name)

    def restructure_files(self, doc_folder_name, target_root_folder):
        """Restructure and rename files based on topic IDs and prepare them for the help system."""
        # Step 1: Unzip files
        renamed_folder_path = find_and_unzip_files(self.source_root, doc_folder_name)
        if not renamed_folder_path:
            logging.warning("No files to process.")
            return

        # Step 2: Copy and rename index.html to toc.html
        copy_and_rename_index(renamed_folder_path, target_root_folder)

        # Step 3: Copy all images from 'graphic' to 'graphics'
        copy_images(renamed_folder_path, target_root_folder)

        # Step 4: Format HTML files to ensure specific tags are on separate lines
        self.format_html_files(target_root_folder)

        # Step 5: Convert toc.html to toc.xml
        transform_toc_html_to_xml(os.path.join(target_root_folder, 'toc.html'), os.path.join(target_root_folder, 'toc.xml'))

    def format_html_files(self, target_root_folder):
        """Format HTML files to ensure specific tags are on separate lines."""
        for dirpath, _, filenames in os.walk(target_root_folder):
            for filename in filenames:
                if filename.endswith('.html'):
                    file_path = os.path.join(dirpath, filename)
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                    formatted_content = format_html(content)
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(formatted_content)
                    logging.info(f"Formatted {filename} to have specific tags on separate lines.")

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, LOGGING_LEVEL),
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename="processing.log",
        filemode="w"
    )
    logging.info("Starting the Help System Processor")

    # Ask for document name and output folder
    use_doc_list = input("Use document list? (y/n): ").strip().lower()
    if use_doc_list == "y":
        doc_list = DOC_LIST
    elif use_doc_list == "n":
        doc_folder_name = input("Enter the name of the document folder: ")
        doc_list = [doc_folder_name]
    else:
        logging.error("Invalid option selected. Exiting.")
        exit(1)

    print("Select an output folder option:")
    print("1: _target_html folder")
    print("2: techdocsdev folder")
    option = input("Enter the option number (1 or 2): ").strip()
    if option not in TARGET_ROOT:
        logging.error("Invalid output folder option selected. Exiting.")
        exit(1)

    processor = HelpSystemProcessor(SOURCE_ROOT, TARGET_ROOT, doc_list, option)
    processor.process_documents()
    logging.info("Processing completed.")
