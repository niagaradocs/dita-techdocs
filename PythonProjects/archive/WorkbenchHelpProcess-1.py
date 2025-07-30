{
    "chunks": [
        {
            "type": "txt",
            "chunk_number": 1,
            "lines": [
                {
                    "line_number": 1,
                    "text": "\"\"\""
                },
                {
                    "line_number": 2,
                    "text": "CURRENT VERSION 1.1 Active, 14/01/2025"
                },
                {
                    "line_number": 3,
                    "text": ""
                },
                {
                    "line_number": 4,
                    "text": "This script processes DITA-OT HTML5 output to prepare files for a custom help system by:"
                },
                {
                    "line_number": 5,
                    "text": ""
                },
                {
                    "line_number": 6,
                    "text": "1. Asking user for options: Use a pre-defined list or enter a single document name."
                },
                {
                    "line_number": 7,
                    "text": "a. User can select between two target folders: c:\\_target_html or c:\\niagara\\techdocsdev."
                },
                {
                    "line_number": 8,
                    "text": "2. Locating appropriate zip file(s) and extracting contents into the target folder for processing."
                },
                {
                    "line_number": 9,
                    "text": "3. Copying and renaming HTML files based on topic IDs, organizing images into a 'graphics' folder, and renaming the legal page to 'index.html'."
                },
                {
                    "line_number": 10,
                    "text": "4. Renaming the existing 'index.html' to 'toc.html' and updating all internal links to match the new file structure."
                },
                {
                    "line_number": 11,
                    "text": "5. Converting 'toc.html' into an XML file ('toc.xml'), adhering to the help system's formatting requirements, while ensuring all list elements are properly nested."
                },
                {
                    "line_number": 12,
                    "text": "6. Updating the section for handling missing or duplicate image names to avoid overwriting."
                },
                {
                    "line_number": 13,
                    "text": "7. Ensuring specified HTML tags are formatted on separate lines for clarity and readability."
                },
                {
                    "line_number": 14,
                    "text": ""
                },
                {
                    "line_number": 15,
                    "text": "\"\"\""
                },
                {
                    "line_number": 16,
                    "text": "import os"
                },
                {
                    "line_number": 17,
                    "text": "import shutil"
                },
                {
                    "line_number": 18,
                    "text": "import re"
                },
                {
                    "line_number": 19,
                    "text": "import zipfile"
                },
                {
                    "line_number": 20,
                    "text": "from bs4 import BeautifulSoup"
                },
                {
                    "line_number": 21,
                    "text": ""
                },
                {
                    "line_number": 22,
                    "text": ""
                },
                {
                    "line_number": 23,
                    "text": "class HelpSystemProcessor:"
                },
                {
                    "line_number": 24,
                    "text": "def __init__(self, source_root, target_base, doc_list, option):"
                },
                {
                    "line_number": 25,
                    "text": "self.source_root = source_root"
                },
                {
                    "line_number": 26,
                    "text": "self.target_base = target_base"
                },
                {
                    "line_number": 27,
                    "text": "self.doc_list = doc_list"
                },
                {
                    "line_number": 28,
                    "text": "self.option = option"
                },
                {
                    "line_number": 29,
                    "text": "self.file_name_mapping = {}"
                },
                {
                    "line_number": 30,
                    "text": "self.image_count = {}"
                },
                {
                    "line_number": 31,
                    "text": ""
                },
                {
                    "line_number": 32,
                    "text": "def process_documents(self):"
                },
                {
                    "line_number": 33,
                    "text": "\"\"\"Main entry point to process each document in the list.\"\"\""
                },
                {
                    "line_number": 34,
                    "text": "for doc_folder_name in self.doc_list:"
                },
                {
                    "line_number": 35,
                    "text": "print(f\"Processing document folder: {doc_folder_name}\")"
                },
                {
                    "line_number": 36,
                    "text": "target_root_folder = self._get_target_root_folder(doc_folder_name)"
                },
                {
                    "line_number": 37,
                    "text": "self.restructure_files(doc_folder_name, target_root_folder)"
                },
                {
                    "line_number": 38,
                    "text": ""
                },
                {
                    "line_number": 39,
                    "text": "def _get_target_root_folder(self, doc_folder_name):"
                },
                {
                    "line_number": 40,
                    "text": "\"\"\"Determine target root folder based on the selected option.\"\"\""
                },
                {
                    "line_number": 41,
                    "text": "if self.option == \"2\":"
                },
                {
                    "line_number": 42,
                    "text": "return os.path.join(self.target_base, doc_folder_name, f\"{doc_folder_name}-doc\", \"src\", \"doc\")"
                },
                {
                    "line_number": 43,
                    "text": "else:"
                },
                {
                    "line_number": 44,
                    "text": "return os.path.join(self.target_base, doc_folder_name)"
                },
                {
                    "line_number": 45,
                    "text": ""
                },
                {
                    "line_number": 46,
                    "text": "def restructure_files(self, doc_folder_name, target_root_folder):"
                },
                {
                    "line_number": 47,
                    "text": "\"\"\"Restructure and rename files based on topic IDs and prepare them for the help system.\"\"\""
                },
                {
                    "line_number": 48,
                    "text": "# Step 1: Unzip files"
                },
                {
                    "line_number": 49,
                    "text": "renamed_folder_path = self.find_and_unzip_files(doc_folder_name)"
                },
                {
                    "line_number": 50,
                    "text": "if not renamed_folder_path:"
                },
                {
                    "line_number": 51,
                    "text": "print(\"No files to process.\")"
                },
                {
                    "line_number": 52,
                    "text": "return"
                },
                {
                    "line_number": 53,
                    "text": ""
                },
                {
                    "line_number": 54,
                    "text": "# Step 2: Copy and rename index.html to toc.html"
                },
                {
                    "line_number": 55,
                    "text": "self.copy_and_rename_index(renamed_folder_path, target_root_folder)"
                },
                {
                    "line_number": 56,
                    "text": ""
                },
                {
                    "line_number": 57,
                    "text": "# Step 3: Copy images from 'graphics' folder to the target 'graphics' folder"
                },
                {
                    "line_number": 58,
                    "text": "self.copy_images(renamed_folder_path, target_root_folder)"
                },
                {
                    "line_number": 59,
                    "text": ""
                },
                {
                    "line_number": 60,
                    "text": "# Step 4: Rename HTML files based on topic IDs and update mapping"
                },
                {
                    "line_number": 61,
                    "text": "self.rename_html_files(renamed_folder_path, target_root_folder)"
                },
                {
                    "line_number": 62,
                    "text": ""
                },
                {
                    "line_number": 63,
                    "text": "# Step 5: Update links in HTML files"
                },
                {
                    "line_number": 64,
                    "text": "self.update_links_in_html(target_root_folder)"
                },
                {
                    "line_number": 65,
                    "text": ""
                },
                {
                    "line_number": 66,
                    "text": "# Step 6: Format HTML files to ensure specific tags are on separate lines"
                },
                {
                    "line_number": 67,
                    "text": "self.format_html_files(target_root_folder)"
                },
                {
                    "line_number": 68,
                    "text": ""
                },
                {
                    "line_number": 69,
                    "text": "# Step 7: Remove unused images"
                },
                {
                    "line_number": 70,
                    "text": "self.remove_unused_images(target_root_folder)"
                },
                {
                    "line_number": 71,
                    "text": ""
                },
                {
                    "line_number": 72,
                    "text": "# Step 8: Convert toc.html to toc.xml"
                },
                {
                    "line_number": 73,
                    "text": "self.transform_toc_html_to_xml(target_root_folder)"
                },
                {
                    "line_number": 74,
                    "text": ""
                },
                {
                    "line_number": 75,
                    "text": "def find_and_unzip_files(self, doc_folder_name):"
                },
                {
                    "line_number": 76,
                    "text": "\"\"\"Find zip files matching doc_folder_name and unzip only html5 contents into its own folder.\"\"\""
                },
                {
                    "line_number": 77,
                    "text": "zip_files = [f for f in os.listdir(self.source_root) if f.endswith('.zip') and f.startswith(doc_folder_name)]"
                },
                {
                    "line_number": 78,
                    "text": ""
                },
                {
                    "line_number": 79,
                    "text": "if not zip_files:"
                },
                {
                    "line_number": 80,
                    "text": "print(f\"No zip files found in {self.source_root} with the prefix '{doc_folder_name}'.\")"
                },
                {
                    "line_number": 81,
                    "text": "return None"
                },
                {
                    "line_number": 82,
                    "text": ""
                },
                {
                    "line_number": 83,
                    "text": "doc_folder_path = os.path.join(self.source_root, doc_folder_name)"
                },
                {
                    "line_number": 84,
                    "text": "os.makedirs(doc_folder_path, exist_ok=True)"
                },
                {
                    "line_number": 85,
                    "text": ""
                },
                {
                    "line_number": 86,
                    "text": "for zip_file in zip_files:"
                },
                {
                    "line_number": 87,
                    "text": "zip_file_path = os.path.join(self.source_root, zip_file)"
                },
                {
                    "line_number": 88,
                    "text": ""
                },
                {
                    "line_number": 89,
                    "text": "with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:"
                },
                {
                    "line_number": 90,
                    "text": "for member in zip_ref.namelist():"
                },
                {
                    "line_number": 91,
                    "text": "if member.startswith('ot-output/html5/'):"
                },
                {
                    "line_number": 92,
                    "text": "target_path = os.path.join(doc_folder_path, member.replace('ot-output/html5/', '', 1))"
                },
                {
                    "line_number": 93,
                    "text": "os.makedirs(os.path.dirname(target_path), exist_ok=True)"
                },
                {
                    "line_number": 94,
                    "text": ""
                },
                {
                    "line_number": 95,
                    "text": "# Correctly handle source file stream as binary"
                },
                {
                    "line_number": 96,
                    "text": "with zip_ref.open(member) as source:"
                },
                {
                    "line_number": 97,
                    "text": "with open(target_path, \"wb\") as target:"
                },
                {
                    "line_number": 98,
                    "text": "# Ensure that the source is read as bytes"
                },
                {
                    "line_number": 99,
                    "text": "if isinstance(source, bytes):"
                },
                {
                    "line_number": 100,
                    "text": "target.write(source)"
                },
                {
                    "line_number": 101,
                    "text": "else:"
                },
                {
                    "line_number": 102,
                    "text": "shutil.copyfileobj(source, target)"
                },
                {
                    "line_number": 103,
                    "text": ""
                },
                {
                    "line_number": 104,
                    "text": "print(f\"Extracted contents of 'html5' from {zip_file} to {doc_folder_path}.\")"
                },
                {
                    "line_number": 105,
                    "text": ""
                },
                {
                    "line_number": 106,
                    "text": "return doc_folder_path"
                },
                {
                    "line_number": 107,
                    "text": ""
                },
                {
                    "line_number": 108,
                    "text": "def copy_and_rename_index(self, renamed_folder_path, target_root_folder):"
                },
                {
                    "line_number": 109,
                    "text": "\"\"\"Copy and rename index.html to toc.html.\"\"\""
                },
                {
                    "line_number": 110,
                    "text": "index_path = os.path.join(renamed_folder_path, 'index.html')"
                },
                {
                    "line_number": 111,
                    "text": "if os.path.exists(index_path):"
                },
                {
                    "line_number": 112,
                    "text": "toc_path = os.path.join(target_root_folder, 'toc.html')"
                },
                {
                    "line_number": 113,
                    "text": "shutil.copy(index_path, toc_path)"
                },
                {
                    "line_number": 114,
                    "text": "print(f\"Copied and renamed 'index.html' to 'toc.html' in {target_root_folder}\")"
                },
                {
                    "line_number": 115,
                    "text": ""
                },
                {
                    "line_number": 116,
                    "text": "def copy_images(self, renamed_folder_path, target_root_folder):"
                },
                {
                    "line_number": 117,
                    "text": "\"\"\"Copy image files to a graphics folder in the target directory.\"\"\""
                },
                {
                    "line_number": 118,
                    "text": "graphics_folder = os.path.join(target_root_folder, 'graphics')"
                },
                {
                    "line_number": 119,
                    "text": "os.makedirs(graphics_folder, exist_ok=True)"
                },
                {
                    "line_number": 120,
                    "text": "image_extensions = ('.png', '.jpg', '.jpeg', '.gif')"
                },
                {
                    "line_number": 121,
                    "text": ""
                },
                {
                    "line_number": 122,
                    "text": "# Handle 'graphics' folder NOTE SOURCE FOLDER IS 'graphic' NOT 'graphics'"
                },
                {
                    "line_number": 123,
                    "text": "folder_path = os.path.join(renamed_folder_path, 'graphic')"
                },
                {
                    "line_number": 124,
                    "text": "if os.path.exists(folder_path):"
                },
                {
                    "line_number": 125,
                    "text": "for dirpath, _, filenames in os.walk(folder_path):"
                },
                {
                    "line_number": 126,
                    "text": "for filename in filenames:"
                },
                {
                    "line_number": 127,
                    "text": "if filename.lower().endswith(image_extensions):"
                },
                {
                    "line_number": 128,
                    "text": "base_filename, file_extension = os.path.splitext(filename)"
                },
                {
                    "line_number": 129,
                    "text": "counter = self.image_count.get(base_filename, 0)"
                },
                {
                    "line_number": 130,
                    "text": ""
                },
                {
                    "line_number": 131,
                    "text": "# Handle duplicate image names"
                },
                {
                    "line_number": 132,
                    "text": "while counter > 0:"
                },
                {
                    "line_number": 133,
                    "text": "new_filename = f\"{base_filename}_{counter}{file_extension}\""
                },
                {
                    "line_number": 134,
                    "text": "if new_filename in filenames:"
                },
                {
                    "line_number": 135,
                    "text": "counter += 1"
                },
                {
                    "line_number": 136,
                    "text": "else:"
                },
                {
                    "line_number": 137,
                    "text": "break"
                },
                {
                    "line_number": 138,
                    "text": ""
                },
                {
                    "line_number": 139,
                    "text": "if counter > 0:"
                },
                {
                    "line_number": 140,
                    "text": "filename = f\"{base_filename}_{counter}{file_extension}\""
                },
                {
                    "line_number": 141,
                    "text": ""
                },
                {
                    "line_number": 142,
                    "text": "shutil.copy(os.path.join(dirpath, filename), os.path.join(graphics_folder, filename))"
                },
                {
                    "line_number": 143,
                    "text": "self.image_count[base_filename] = counter + 1"
                },
                {
                    "line_number": 144,
                    "text": ""
                },
                {
                    "line_number": 145,
                    "text": "def rename_html_files(self, renamed_folder_path, target_root_folder):"
                },
                {
                    "line_number": 146,
                    "text": "\"\"\"Rename HTML files based on topic IDs.\"\"\""
                },
                {
                    "line_number": 147,
                    "text": "for dirpath, _, filenames in os.walk(renamed_folder_path):"
                },
                {
                    "line_number": 148,
                    "text": "for filename in filenames:"
                },
                {
                    "line_number": 149,
                    "text": "if filename.endswith('.html'):"
                },
                {
                    "line_number": 150,
                    "text": "html_file_path = os.path.join(dirpath, filename)"
                },
                {
                    "line_number": 151,
                    "text": "new_filename = self.rename_html_file_based_on_topic_id(html_file_path, target_root_folder, filename)"
                },
                {
                    "line_number": 152,
                    "text": "if new_filename:"
                },
                {
                    "line_number": 153,
                    "text": "self.file_name_mapping[filename] = new_filename"
                },
                {
                    "line_number": 154,
                    "text": ""
                },
                {
                    "line_number": 155,
                    "text": "def rename_html_file_based_on_topic_id(self, html_file_path, target_root_folder, original_filename):"
                },
                {
                    "line_number": 156,
                    "text": "\"\"\"Renames the HTML file based on its topic ID extracted from the <body> or <html> tag.\"\"\""
                },
                {
                    "line_number": 157,
                    "text": "try:"
                },
                {
                    "line_number": 158,
                    "text": "with open(html_file_path, 'r', encoding='utf-8') as file:"
                },
                {
                    "line_number": 159,
                    "text": "soup = BeautifulSoup(file, 'html.parser')"
                },
                {
                    "line_number": 160,
                    "text": "except Exception as e:"
                },
                {
                    "line_number": 161,
                    "text": "print(f\"Error reading {html_file_path}: {e}\")"
                },
                {
                    "line_number": 162,
                    "text": "return None"
                },
                {
                    "line_number": 163,
                    "text": ""
                },
                {
                    "line_number": 164,
                    "text": "topic_id = soup.body.get('id', None) or soup.html.get('id', None)"
                },
                {
                    "line_number": 165,
                    "text": ""
                },
                {
                    "line_number": 166,
                    "text": "if topic_id:"
                },
                {
                    "line_number": 167,
                    "text": "new_file_name = f\"{topic_id}.html\""
                },
                {
                    "line_number": 168,
                    "text": "new_file_path = os.path.join(target_root_folder, new_file_name)"
                },
                {
                    "line_number": 169,
                    "text": "shutil.copy(html_file_path, new_file_path)"
                },
                {
                    "line_number": 170,
                    "text": "return new_file_name"
                },
                {
                    "line_number": 171,
                    "text": "return None"
                },
                {
                    "line_number": 172,
                    "text": ""
                },
                {
                    "line_number": 173,
                    "text": "def update_links_in_html(self, target_root_folder):"
                },
                {
                    "line_number": 174,
                    "text": "\"\"\"Update links in HTML files to match the new file structure.\"\"\""
                },
                {
                    "line_number": 175,
                    "text": "for dirpath, _, filenames in os.walk(target_root_folder):"
                },
                {
                    "line_number": 176,
                    "text": "for filename in filenames:"
                },
                {
                    "line_number": 177,
                    "text": "if filename.endswith('.html'):"
                },
                {
                    "line_number": 178,
                    "text": "file_path = os.path.join(dirpath, filename)"
                },
                {
                    "line_number": 179,
                    "text": "with open(file_path, 'r', encoding='utf-8') as file:"
                },
                {
                    "line_number": 180,
                    "text": "content = file.read()"
                },
                {
                    "line_number": 181,
                    "text": ""
                },
                {
                    "line_number": 182,
                    "text": "updated_content = re.sub(r'((href|src)=\\\")([^\\\"]+)(\\\")',"
                },
                {
                    "line_number": 183,
                    "text": "lambda m: f'{m.group(1)}{self.update_links(m.group(3))}{m.group(4)}',"
                },
                {
                    "line_number": 184,
                    "text": "content)"
                },
                {
                    "line_number": 185,
                    "text": ""
                },
                {
                    "line_number": 186,
                    "text": "with open(file_path, 'w', encoding='utf-8') as file:"
                },
                {
                    "line_number": 187,
                    "text": "file.write(updated_content)"
                },
                {
                    "line_number": 188,
                    "text": "print(f\"Updated internal links in {filename}.\")"
                },
                {
                    "line_number": 189,
                    "text": ""
                },
                {
                    "line_number": 190,
                    "text": "def update_links(self, link):"
                },
                {
                    "line_number": 191,
                    "text": "\"\"\"Update a link based on the file name mapping.\"\"\""
                },
                {
                    "line_number": 192,
                    "text": "if link.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):"
                },
                {
                    "line_number": 193,
                    "text": "return f'graphics/{os.path.basename(link)}'"
                },
                {
                    "line_number": 194,
                    "text": "elif link.lower().endswith('.html'):"
                },
                {
                    "line_number": 195,
                    "text": "base_name = os.path.basename(link)"
                },
                {
                    "line_number": 196,
                    "text": "return self.file_name_mapping.get(base_name, base_name)"
                },
                {
                    "line_number": 197,
                    "text": "else:"
                },
                {
                    "line_number": 198,
                    "text": "return link"
                },
                {
                    "line_number": 199,
                    "text": ""
                },
                {
                    "line_number": 200,
                    "text": "def format_html_files(self, target_root_folder):"
                },
                {
                    "line_number": 201,
                    "text": "\"\"\"Ensure <head>, </head>, <title>, </title>, <body>, and </body> tags are on separate lines in all HTML files.\"\"\""
                },
                {
                    "line_number": 202,
                    "text": "for dirpath, _, filenames in os.walk(target_root_folder):"
                },
                {
                    "line_number": 203,
                    "text": "for filename in filenames:"
                },
                {
                    "line_number": 204,
                    "text": "if filename.endswith('.html') or filename == 'toc.html':"
                },
                {
                    "line_number": 205,
                    "text": "file_path = os.path.join(dirpath, filename)"
                },
                {
                    "line_number": 206,
                    "text": "with open(file_path, 'r', encoding='utf-8') as file:"
                },
                {
                    "line_number": 207,
                    "text": "content = file.read()"
                },
                {
                    "line_number": 208,
                    "text": ""
                },
                {
                    "line_number": 209,
                    "text": "# Ensure specified tags are on separate lines"
                },
                {
                    "line_number": 210,
                    "text": "content = re.sub(r'(\\s*<head>)', r'\\n\\1\\n', content)"
                },
                {
                    "line_number": 211,
                    "text": "content = re.sub(r'(</head>)', r'\\n\\1\\n', content)"
                },
                {
                    "line_number": 212,
                    "text": "content = re.sub(r'(\\s*<title>)', r'\\n\\1\\n', content)"
                },
                {
                    "line_number": 213,
                    "text": "content = re.sub(r'(</title>)', r'\\n\\1\\n', content)"
                },
                {
                    "line_number": 214,
                    "text": "content = re.sub(r'(\\s*<body[^>]*>)', r'\\n\\1\\n', content)"
                },
                {
                    "line_number": 215,
                    "text": "content = re.sub(r'(</body>)', r'\\n\\1\\n', content)"
                },
                {
                    "line_number": 216,
                    "text": ""
                },
                {
                    "line_number": 217,
                    "text": "with open(file_path, 'w', encoding='utf-8') as file:"
                },
                {
                    "line_number": 218,
                    "text": "file.write(content)"
                },
                {
                    "line_number": 219,
                    "text": "print(f\"Formatted {filename} to have specific tags on separate lines.\")"
                },
                {
                    "line_number": 220,
                    "text": ""
                },
                {
                    "line_number": 221,
                    "text": "def remove_unused_images(self, target_root_folder):"
                },
                {
                    "line_number": 222,
                    "text": "\"\"\"Remove images in the 'graphics' folder that are not referenced in any HTML file.\"\"\""
                },
                {
                    "line_number": 223,
                    "text": ""
                },
                {
                    "line_number": 224,
                    "text": "graphics_folder = os.path.join(target_root_folder, 'graphics')"
                },
                {
                    "line_number": 225,
                    "text": "if not os.path.exists(graphics_folder):"
                },
                {
                    "line_number": 226,
                    "text": "print(\"Graphics folder does not exist, skipping cleanup.\")"
                },
                {
                    "line_number": 227,
                    "text": "return"
                },
                {
                    "line_number": 228,
                    "text": ""
                },
                {
                    "line_number": 229,
                    "text": "# Collect all image references from HTML files"
                },
                {
                    "line_number": 230,
                    "text": "used_images = set()"
                },
                {
                    "line_number": 231,
                    "text": "for dirpath, _, filenames in os.walk(target_root_folder):"
                },
                {
                    "line_number": 232,
                    "text": "for filename in filenames:"
                },
                {
                    "line_number": 233,
                    "text": "if filename.endswith('.html'):"
                },
                {
                    "line_number": 234,
                    "text": "file_path = os.path.join(dirpath, filename)"
                },
                {
                    "line_number": 235,
                    "text": "try:"
                },
                {
                    "line_number": 236,
                    "text": "with open(file_path, 'r', encoding='utf-8') as file:"
                },
                {
                    "line_number": 237,
                    "text": "soup = BeautifulSoup(file, 'html.parser')"
                },
                {
                    "line_number": 238,
                    "text": ""
                },
                {
                    "line_number": 239,
                    "text": "# Find all image tags"
                },
                {
                    "line_number": 240,
                    "text": "for img in soup.find_all('img'):"
                },
                {
                    "line_number": 241,
                    "text": "src = img.get('src')"
                },
                {
                    "line_number": 242,
                    "text": "if src:"
                },
                {
                    "line_number": 243,
                    "text": "image_name = os.path.basename(src)"
                },
                {
                    "line_number": 244,
                    "text": "used_images.add(image_name)"
                },
                {
                    "line_number": 245,
                    "text": ""
                },
                {
                    "line_number": 246,
                    "text": "except Exception as e:"
                },
                {
                    "line_number": 247,
                    "text": "print(f\"Error processing {file_path}: {e}\")"
                },
                {
                    "line_number": 248,
                    "text": ""
                },
                {
                    "line_number": 249,
                    "text": "# Get list of all images in the graphics folder"
                },
                {
                    "line_number": 250,
                    "text": "all_images = {img for img in os.listdir(graphics_folder) if img.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))}"
                },
                {
                    "line_number": 251,
                    "text": ""
                },
                {
                    "line_number": 252,
                    "text": "# Find unused images"
                },
                {
                    "line_number": 253,
                    "text": "unused_images = all_images - used_images"
                },
                {
                    "line_number": 254,
                    "text": ""
                },
                {
                    "line_number": 255,
                    "text": "# Remove unused images"
                },
                {
                    "line_number": 256,
                    "text": "for img in unused_images:"
                },
                {
                    "line_number": 257,
                    "text": "img_path = os.path.join(graphics_folder, img)"
                },
                {
                    "line_number": 258,
                    "text": "try:"
                },
                {
                    "line_number": 259,
                    "text": "os.remove(img_path)"
                },
                {
                    "line_number": 260,
                    "text": "print(f\"Deleted unused image: {img}\")"
                },
                {
                    "line_number": 261,
                    "text": "except Exception as e:"
                },
                {
                    "line_number": 262,
                    "text": "print(f\"Error deleting {img}: {e}\")"
                },
                {
                    "line_number": 263,
                    "text": ""
                },
                {
                    "line_number": 264,
                    "text": "print(\"Unused image cleanup completed.\")"
                },
                {
                    "line_number": 265,
                    "text": ""
                },
                {
                    "line_number": 266,
                    "text": "def transform_toc_html_to_xml(self, target_root_folder):"
                },
                {
                    "line_number": 267,
                    "text": "\"\"\"Convert toc.html to a formatted toc.xml using the provided structure, and then delete toc.html.\"\"\""
                },
                {
                    "line_number": 268,
                    "text": "toc_html_path = os.path.join(target_root_folder, 'toc.html')"
                },
                {
                    "line_number": 269,
                    "text": "toc_xml_path = os.path.join(target_root_folder, 'toc.xml')"
                },
                {
                    "line_number": 270,
                    "text": "legal_page_path = os.path.join(target_root_folder, 'legal_niagara_tridium.html')"
                },
                {
                    "line_number": 271,
                    "text": "index_path = os.path.join(target_root_folder, 'index.html')"
                },
                {
                    "line_number": 272,
                    "text": ""
                },
                {
                    "line_number": 273,
                    "text": "if not os.path.exists(toc_html_path):"
                },
                {
                    "line_number": 274,
                    "text": "print(\"toc.html not found for conversion.\")"
                },
                {
                    "line_number": 275,
                    "text": "return"
                },
                {
                    "line_number": 276,
                    "text": ""
                },
                {
                    "line_number": 277,
                    "text": "try:"
                },
                {
                    "line_number": 278,
                    "text": "with open(toc_html_path, 'r', encoding='utf-8') as file:"
                },
                {
                    "line_number": 279,
                    "text": "soup = BeautifulSoup(file, 'html.parser')"
                },
                {
                    "line_number": 280,
                    "text": ""
                },
                {
                    "line_number": 281,
                    "text": "toc_items = self.parse_ul(soup.find('ul'), '')"
                },
                {
                    "line_number": 282,
                    "text": ""
                },
                {
                    "line_number": 283,
                    "text": "# Check if toc_items is empty before processing"
                },
                {
                    "line_number": 284,
                    "text": "if not toc_items.strip():"
                },
                {
                    "line_number": 285,
                    "text": "raise ValueError(\"Error: 'toc.html' generated no items. Cannot proceed.\")"
                },
                {
                    "line_number": 286,
                    "text": ""
                },
                {
                    "line_number": 287,
                    "text": "# Prepare the initial XML content"
                },
                {
                    "line_number": 288,
                    "text": "toc_content = '<?xml version=\"1.0\" encoding=\"UTF-8\"?>\\n<toc>\\n'"
                },
                {
                    "line_number": 289,
                    "text": ""
                },
                {
                    "line_number": 290,
                    "text": "# Check the first line and make necessary adjustments for the legal item"
                },
                {
                    "line_number": 291,
                    "text": "lines = toc_items.splitlines()"
                },
                {
                    "line_number": 292,
                    "text": "first_line = lines[0].strip() if lines else \"\""
                },
                {
                    "line_number": 293,
                    "text": ""
                },
                {
                    "line_number": 294,
                    "text": "# Determine the proper format for the Legal Notice tocitem"
                },
                {
                    "line_number": 295,
                    "text": "if first_line == '<tocitem target=\"index.html\" text=\"Legal Notice\">':"
                },
                {
                    "line_number": 296,
                    "text": "toc_content += toc_items + '</tocitem>'  # Properly close"
                },
                {
                    "line_number": 297,
                    "text": ""
                },
                {
                    "line_number": 298,
                    "text": "elif first_line == '<tocitem target=\"legal_niagara_tridium.html\" text=\"Legal Notice\">':"
                },
                {
                    "line_number": 299,
                    "text": "lines[0] = '<tocitem target=\"index.html\" text=\"Legal Notice\">'  # Change opening tag"
                },
                {
                    "line_number": 300,
                    "text": "toc_content += '\\n'.join(lines) + '</tocitem>'  # Properly close"
                },
                {
                    "line_number": 301,
                    "text": ""
                },
                {
                    "line_number": 302,
                    "text": "else:"
                },
                {
                    "line_number": 303,
                    "text": "if not first_line.startswith('<tocitem '):"
                },
                {
                    "line_number": 304,
                    "text": "raise ValueError(\"Error: Unexpected content found; expected <tocitem> format.\")"
                },
                {
                    "line_number": 305,
                    "text": "toc_content += '<tocitem target=\"index.html\" text=\"Legal Notice\"></tocitem>\\n' + toc_items"
                },
                {
                    "line_number": 306,
                    "text": ""
                },
                {
                    "line_number": 307,
                    "text": "# Close the toc element"
                },
                {
                    "line_number": 308,
                    "text": "toc_content += '</toc>'"
                },
                {
                    "line_number": 309,
                    "text": ""
                },
                {
                    "line_number": 310,
                    "text": "with open(toc_xml_path, 'w', encoding='utf-8') as file:"
                },
                {
                    "line_number": 311,
                    "text": "file.write(toc_content)"
                },
                {
                    "line_number": 312,
                    "text": "print(\"toc.xml created successfully.\")"
                },
                {
                    "line_number": 313,
                    "text": ""
                },
                {
                    "line_number": 314,
                    "text": "os.remove(toc_html_path)"
                },
                {
                    "line_number": 315,
                    "text": "print(\"toc.html has been deleted after conversion.\")"
                },
                {
                    "line_number": 316,
                    "text": ""
                },
                {
                    "line_number": 317,
                    "text": "# Check for existing index.html and delete it if it exists"
                },
                {
                    "line_number": 318,
                    "text": "if os.path.exists(index_path):"
                },
                {
                    "line_number": 319,
                    "text": "os.remove(index_path)"
                },
                {
                    "line_number": 320,
                    "text": "print(\"Deleted existing index.html before renaming.\")"
                },
                {
                    "line_number": 321,
                    "text": ""
                },
                {
                    "line_number": 322,
                    "text": "# Renaming legal_niagara_tridium.html to index.html"
                },
                {
                    "line_number": 323,
                    "text": "if os.path.exists(legal_page_path):"
                },
                {
                    "line_number": 324,
                    "text": "os.rename(legal_page_path, index_path)"
                },
                {
                    "line_number": 325,
                    "text": "print(\"Renamed legal_niagara_tridium.html to index.html.\")"
                },
                {
                    "line_number": 326,
                    "text": "else:"
                },
                {
                    "line_number": 327,
                    "text": "print(\"legal_niagara_tridium.html not found for renaming.\")"
                },
                {
                    "line_number": 328,
                    "text": ""
                },
                {
                    "line_number": 329,
                    "text": "except Exception as e:"
                },
                {
                    "line_number": 330,
                    "text": "print(f\"An error occurred during toc.xml creation: {e}\")"
                },
                {
                    "line_number": 331,
                    "text": ""
                },
                {
                    "line_number": 332,
                    "text": "def parse_ul(self, ul, indent):"
                },
                {
                    "line_number": 333,
                    "text": "\"\"\"Parse the <ul> elements to create the corresponding toc.xml structure.\"\"\""
                },
                {
                    "line_number": 334,
                    "text": "items_xml = ''"
                },
                {
                    "line_number": 335,
                    "text": "for li in ul.find_all('li', recursive=False):"
                },
                {
                    "line_number": 336,
                    "text": "a = li.find('a')"
                },
                {
                    "line_number": 337,
                    "text": "if a:"
                },
                {
                    "line_number": 338,
                    "text": "href = a.get('href')"
                },
                {
                    "line_number": 339,
                    "text": "text = a.get_text(strip=True)"
                },
                {
                    "line_number": 340,
                    "text": "items_xml += f'{indent}<tocitem target=\"{href}\" text=\"{text}\">\\n'"
                },
                {
                    "line_number": 341,
                    "text": "child_ul = li.find('ul')"
                },
                {
                    "line_number": 342,
                    "text": "if child_ul:"
                },
                {
                    "line_number": 343,
                    "text": "items_xml += self.parse_ul(child_ul, indent + ' ')"
                },
                {
                    "line_number": 344,
                    "text": "items_xml += f'{indent}</tocitem>\\n'"
                },
                {
                    "line_number": 345,
                    "text": "return items_xml"
                },
                {
                    "line_number": 346,
                    "text": ""
                },
                {
                    "line_number": 347,
                    "text": "# Entry point to run the script"
                },
                {
                    "line_number": 348,
                    "text": "if __name__ == \"__main__\":"
                },
                {
                    "line_number": 349,
                    "text": "source_root_folder = \"C:\\\\Users\\\\e333758\\\\Honeywell\\\\PUBLIC Tridium Tech Docs - Workbench_Help - Documents\\\\_zipfiles\""
                },
                {
                    "line_number": 350,
                    "text": "doc_list = ['docKitControl','docMqtt','docProvisioning','docRdbms']"
                },
                {
                    "line_number": 351,
                    "text": ""
                },
                {
                    "line_number": 352,
                    "text": "# Ask for document name and output folder"
                },
                {
                    "line_number": 353,
                    "text": "use_doc_list = input(\"Use document list? (y/n): \").strip().lower()"
                },
                {
                    "line_number": 354,
                    "text": "if use_doc_list == 'y':"
                },
                {
                    "line_number": 355,
                    "text": "doc_list = doc_list"
                },
                {
                    "line_number": 356,
                    "text": "elif use_doc_list == 'n':"
                },
                {
                    "line_number": 357,
                    "text": "doc_folder_name = input(\"Enter the name of the document folder: \")"
                },
                {
                    "line_number": 358,
                    "text": "doc_list = [doc_folder_name]"
                },
                {
                    "line_number": 359,
                    "text": "else:"
                },
                {
                    "line_number": 360,
                    "text": "print(\"Invalid option selected. Exiting.\")"
                },
                {
                    "line_number": 361,
                    "text": "exit(1)"
                },
                {
                    "line_number": 362,
                    "text": ""
                },
                {
                    "line_number": 363,
                    "text": "print(\"Select an output folder option:\")"
                },
                {
                    "line_number": 364,
                    "text": "print(\"1: '_target_html' folder\")"
                },
                {
                    "line_number": 365,
                    "text": "print(\"2: 'techdocsdev' folder\")"
                },
                {
                    "line_number": 366,
                    "text": "option = input(\"Enter the option number (1 or 2): \")"
                },
                {
                    "line_number": 367,
                    "text": "target_base = \"c:\\\\_target_html\" if option == \"1\" else \"C:\\\\niagara\\\\techdocsdev\\\\docs\""
                },
                {
                    "line_number": 368,
                    "text": ""
                },
                {
                    "line_number": 369,
                    "text": "processor = HelpSystemProcessor(source_root_folder, target_base, doc_list, option)"
                },
                {
                    "line_number": 370,
                    "text": "processor.process_documents()"
                }
            ],
            "token_count": 3827
        }
    ]
}