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
        renamed_folder_path = self.find_and_unzip_files(doc_folder_name)
        if not renamed_folder_path:
            print("No files to process.")
            return

        # Step 2: Copy and rename index.html to toc.html
        self.copy_and_rename_index(renamed_folder_path, target_root_folder)

        # Step 3: Track required images based on reuse references
        needed_images = self.track_reuse_references(target_root_folder, renamed_folder_path)

        # Step 4: Copy images from 'graphics' folder to the target 'graphics' folder
        self.copy_images(renamed_folder_path, target_root_folder, needed_images)

        # Step 5: Remove unnecessary images from the graphics folder
        self.remove_unnecessary_images(target_root_folder, needed_images)

        # Step 6: Rename HTML files based on topic IDs and update mapping
        self.rename_html_files(renamed_folder_path, target_root_folder)

        # Step 7: Update links in HTML files
        self.update_links_in_html(target_root_folder)

        # Step 8: Format HTML files to ensure specific tags are on separate lines
        self.format_html_files(target_root_folder)

        # Step 9: Convert toc.html to toc.xml
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
                        with zip_ref.open(member) as source, open(target_path, "wb") as target:
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

    def track_reuse_references(self, target_root_folder, renamed_folder_path):
        """Track all necessary images from the reuse folder based on references in other files."""
        needed_images = set()
        reuse_folder_path = os.path.join(renamed_folder_path, 'reuse')

        # Step 1: Identify reuse files that are referenced by other files
        for dirpath, _, filenames in os.walk(target_root_folder):
            for filename in filenames:
                if filename.endswith('.html'):
                    file_path = os.path.join(dirpath, filename)
                    content = self._get_file_content(file_path)

                    # Check for references to reuse files (e.g., via href or xref)
                    try:
                        for reuse_file in os.listdir(reuse_folder_path):
                            if reuse_file in content:
                                # Step 2: Check if the reuse file itself references any images
                                reuse_file_path = os.path.join(reuse_folder_path, reuse_file)
                                reuse_content = self._get_file_content(reuse_file_path)
                                if reuse_content:
                                    soup = BeautifulSoup(reuse_content, 'html.parser')
                                    for img_tag in soup.find_all('img'):
                                        img_src = img_tag.get('src')
                                        if img_src.startswith('graphics/'):
                                            needed_images.add(os.path.basename(img_src))
                    except FileNotFoundError:
                        print(f"Warning: Reuse folder '{reuse_folder_path}' not found.")

        return needed_images

    def _get_file_content(self, file_path):
        """Helper method to get the content of a file, with caching to avoid redundant reads."""
        if file_path not in self.cached_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.cached_files[file_path] = file.read()
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                return None
        return self.cached_files.get(file_path)

    def copy_images(self, renamed_folder_path, target_root_folder, needed_images):
        """Copy only necessary image files to a graphics folder in the target directory."""
        graphics_folder = os.path.join(target_root_folder, 'graphics')
        os.makedirs(graphics_folder, exist_ok=True)

        for img_name in needed_images:
            src_path = os.path.join(renamed_folder_path, 'graphics', img_name)
            if os.path.exists(src_path):
                shutil.copy(src_path, os.path.join(graphics_folder, img_name))
                print(f"Copied image {img_name} to target graphics folder.")

    def remove_unnecessary_images(self, target_root_folder, needed_images):
        """Remove unnecessary image files from the target graphics folder."""
        graphics_folder = os.path.join(target_root_folder, 'graphics')
        if not os.path.exists(graphics_folder):
            return

        for img_name in os.listdir(graphics_folder):
            if img_name not in needed_images:
                img_path = os.path.join(graphics_folder, img_name)
                os.remove(img_path)
                print(f"Removed unnecessary image {img_name} from target graphics folder.")

    def rename_html_files(self, renamed_folder_path, target_root_folder):
        """Rename HTML files based on topic IDs."""
        for dirpath, _, filenames in os.walk(renamed_folder_path):
            for filename in filenames:
                if filename.endswith('.html') and filename not in ['index.html', 'WH_LegalNotices_Tridium_N4_0000009932.html']:
                    html_file_path = os.path.join(dirpath, filename)
                    new_filename = self.rename_html_file_based_on_topic_id(html_file_path, target_root_folder, filename)
                    if new_filename:
                        self.file_name_mapping[filename] = new_filename

    def rename_html_file_based_on_topic_id(self, html_file_path, target_root_folder, original_filename):
        """Renames the HTML file based on its topic ID extracted from the <body> or <html> tag."""
        content = self._get_file_content(html_file_path)
        if not content:
            return None

        try:
            soup = BeautifulSoup(content, 'html.parser')
        except Exception as e:
            print(f"Error parsing HTML for {html_file_path}: {e}")
            return None

        topic_id = soup.body.get('id', None) or soup.html.get('id', None)

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
                if filename.endswith('.html'):
                    file_path = os.path.join(dirpath, filename)
                    content = self._get_file_content(file_path)
                    if content:
                        updated_content = re.sub(r'((href|src)=\")([^\"]+)(\")',
                                                 lambda m: f'{m.group(1)}{self.update_links(m.group(3))}{m.group(4)}',
                                                 content)

                        with open(file_path, 'w', encoding='utf-8') as file:
                            file.write(updated_content)
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
                if filename.endswith('.html'):
                    file_path = os.path.join(dirpath, filename)
                    content = self._get_file_content(file_path)
                    if content:
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

    def transform_toc_html_to_xml(self, target_root_folder):
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
            toc_content += self.parse_ul(soup.find('ul'), '')
            toc_content += '</toc>'

            with open(toc_xml_path, 'w', encoding='utf-8') as file:
                file.write(toc_content)
                print("toc.xml created successfully.")

            os.remove(toc_html_path)
            print("toc.html has been deleted after conversion.")

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
