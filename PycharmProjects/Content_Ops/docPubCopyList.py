#  This script is for exporting files from the old/pre-Heretto/4.14 bitbucket repo based on the bookmap
#  It copies the bookmap and all child topics into the target folder for exporting to Heretto
#  Has function to also copy the reuse folder so now all wh topics are copied every time so file can be opened for
#  testing using Arbortext. We don't copy the reuse folder to Heretto.
#  25 July 2024, I altered it to use a list instead of input at runtime.
#  26 July 2024, Added a line to ignore #ID strings after filenames.

import os
import re
import shutil
import openpyxl


def normalize_path(file_path, base_path):
    """Normalize paths by resolving any relative references ('../') and stripping fragment identifiers."""
    # Remove URL fragment identifiers (anything after a '#')
    file_path = file_path.split('#')[0]

    # Check if the path is absolute
    if os.path.isabs(file_path):
        return file_path

    # Create a full path if the path is not absolute
    return os.path.normpath(os.path.join(base_path, file_path))


def extract_referenced_files(bookmap_path, base_path, files_found=None):
    if files_found is None:
        files_found = set()

    normalized_path = normalize_path(bookmap_path, base_path)

    with open(normalized_path, 'r', encoding='utf-8') as file:
        content = file.read()

    file_refs = re.findall(r'href="([^"]+)"', content)
    for ref in file_refs:
        normalized_ref = normalize_path(ref, os.path.dirname(normalized_path))
        if normalized_ref.endswith('.ditamap') and normalized_ref not in files_found:
            extract_referenced_files(normalized_ref, base_path, files_found)
        files_found.add(normalized_ref)

    return files_found


def extract_image_references_from_file(xml_path):
    with open(xml_path, "r", encoding='utf-8') as xml_file:
        xml_content = xml_file.read()
    return re.findall(r'<image\s+href="([^"]+)"', xml_content)


def find_referenced_graphics(source_root, referenced_files):
    referenced_graphics = set()
    for ref_file in referenced_files:
        ref_path = os.path.join(source_root, ref_file)
        if os.path.exists(ref_path) and ref_path.lower().endswith((".xml", ".dita", ".ditamap")):
            image_references = extract_image_references_from_file(ref_path)
            for image_ref in image_references:
                image_full_path = normalize_path(image_ref, os.path.dirname(ref_path))
                referenced_graphics.add(image_full_path)
    return referenced_graphics


def copy_files(referenced_files, source_root, target_root):
    copied_files_count = 0
    for file_path in referenced_files:
        normalized_source_path = normalize_path(file_path, source_root)
        relative_path = os.path.relpath(normalized_source_path, source_root)
        normalized_target_path = os.path.join(target_root, relative_path)
        if not os.path.exists(normalized_source_path):
            print(f"Source file does not exist: {normalized_source_path}")
            continue
        os.makedirs(os.path.dirname(normalized_target_path), exist_ok=True)
        shutil.copy2(normalized_source_path, normalized_target_path)
        copied_files_count += 1
        print(f"Copied and potentially overwritten: {normalized_target_path}")
    return copied_files_count


def main():
    input("Make sure to update your 'docList' and press 'y' to proceed or 'n' to abort...")
    docList = ['docTagging']
    #  docList = ['docJ9MtgWrg', 'docKitControl', 'docLinuxN4', 'docN4Install', 'docHttpClient', 'docJ9BackupRestore']

    for docName in docList:
        print(f"Processing {docName}")
        source_root = "c:\\repos\\dita-niagara"
        target_root = os.path.join("C:\\_publication", docName)
        if not os.path.exists(target_root):
            os.makedirs(target_root)
        bookmap_file_name = f"{docName}.ditamap"
        bookmap_path = os.path.join(source_root, bookmap_file_name)
        if not os.path.exists(bookmap_path):
            print(f"Bookmap file not found: {bookmap_path}")
            continue
        referenced_files = extract_referenced_files(bookmap_path, source_root)
        referenced_graphics = find_referenced_graphics(source_root, referenced_files)
        all_referenced_files = {bookmap_file_name}.union(referenced_files, referenced_graphics)
        copied_files_count = copy_files(all_referenced_files, source_root, target_root)
        print(f"Copy completed. {copied_files_count} files were copied for {docName}.")


if __name__ == "__main__":
    main()
