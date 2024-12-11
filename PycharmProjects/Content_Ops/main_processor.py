import os
import re
import shutil
from file_utils import (
    find_and_unzip_files,
    copy_and_rename_index,
    copy_images,
)
from html_utils import transform_toc_html_to_xml, format_html


class HelpSystemProcessor:
    def __init__(self, source_root, target_root, doc_list, option):
        self.source_root = source_root
        self.target_root = target_root
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
        return os.path.join(self.target_root, doc_folder_name)

    def restructure_files(self, doc_folder_name, target_root_folder):
        """Restructure and rename files based on topic IDs and prepare them for the help system."""
        # Step 1: Unzip files
        base_folder_path = find_and_unzip_files(self.source_root, doc_folder_name)
        if not base_folder_path:
            print("No files to process.")
            return

        # Append 'ot-output/html5' to the base folder path
        html5_folder_path = os.path.join(base_folder_path, "ot-output", "html5")
        if not os.path.exists(html5_folder_path):
            print(f"Error: Expected 'html5' folder not found at {html5_folder_path}.")
            return

        print(f"HTML5 folder found at: {html5_folder_path}")

        # Step 2: Copy and rename index.html to toc.html
        copy_and_rename_index(html5_folder_path, target_root_folder)

        # Step 3: Copy images from 'graphic' folder to the target 'graphics' folder
        copy_images(html5_folder_path, target_root_folder)

        # Step 4: Rename HTML files based on topic IDs
        self.rename_html_files(html5_folder_path, target_root_folder)

        # Step 5: Update links in HTML files
        self.update_links_in_html(target_root_folder)

        # Step 6: Format HTML files to ensure specific tags are on separate lines
        self.format_html_files(target_root_folder)

        # Step 7: Convert toc.html to toc.xml
        transform_toc_html_to_xml(
            os.path.join(target_root_folder, "toc.html"),
            os.path.join(target_root_folder, "toc.xml"),
        )

    def rename_html_files(self, renamed_folder_path, target_root_folder):
        """Rename HTML files based on topic IDs."""
        for dirpath, _, filenames in os.walk(renamed_folder_path):
            for filename in filenames:
                if filename.endswith(".html") and filename not in [
                    "index.html",
                    "WH_LegalNotices_Tridium_N4_0000009932.html",
                ]:
                    html_file_path = os.path.join(dirpath, filename)
                    new_filename = self.rename_html_file_based_on_topic_id(
                        html_file_path, target_root_folder, filename
                    )
                    if new_filename:
                        self.file_name_mapping[filename] = new_filename

    def rename_html_file_based_on_topic_id(
        self, html_file_path, target_root_folder, original_filename
    ):
        """Renames the HTML file based on its topic ID extracted from the <body> or <html> tag."""
        with open(html_file_path, "r", encoding="utf-8") as file:
            content = file.read()

        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(content, "html.parser")
        except Exception as e:
            print(f"Error parsing HTML for {html_file_path}: {e}")
            return None

        topic_id = soup.body.get("id", None) or soup.html.get("id", None)

        if topic_id:
            new_file_name = f"{topic_id}.html"
            new_file_path = os.path.join(target_root_folder, new_file_name)
            shutil.copy(html_file_path, new_file_path)
            print(f"Renamed HTML file {original_filename} to {new_file_name}")
            return new_file_name
        return None

    def update_links_in_html(self, target_root_folder):
        """Update links in HTML files to match the new file structure."""
        for dirpath, _, filenames in os.walk(target_root_folder):
            for filename in filenames:
                if filename.endswith(".html"):
                    file_path = os.path.join(dirpath, filename)
                    with open(file_path, "r", encoding="utf-8") as file:
                        content = file.read()

                    updated_content = re.sub(
                        r'(?P<attr>(href|src)=["\'])(?P<url>.*?)(["\'])',
                        lambda m: f"{m.group('attr')}{self.update_links(m.group('url'))}{m.group(4)}",
                        content,
                    )

                    with open(file_path, "w", encoding="utf-8") as file:
                        file.write(updated_content)
                    print(f"Updated internal links in {filename}.")

    def update_links(self, link):
        """Update a link based on the file name mapping."""
        if link.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
            return f"graphics/{os.path.basename(link)}"
        elif link.lower().endswith(".html"):
            base_name = os.path.basename(link)
            return self.file_name_mapping.get(base_name, base_name)
        else:
            return link

    def format_html_files(self, target_root_folder):
        """Ensure <head>, </head>, <title>, </title>, <body>, and </body> tags are on separate lines in all HTML files."""
        for dirpath, _, filenames in os.walk(target_root_folder):
            for filename in filenames:
                if filename.endswith(".html"):
                    file_path = os.path.join(dirpath, filename)
                    with open(file_path, "r", encoding="utf-8") as file:
                        content = file.read()

                    formatted_content = format_html(content)

                    with open(file_path, "w", encoding="utf-8") as file:
                        file.write(formatted_content)
                    print(f"Formatted {filename} to have specific tags on separate lines.")


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

    processor = HelpSystemProcessor(source_root, target_root[option], documents_to_process, option)
    processor.process_documents()
