import os
import shutil
from bs4 import BeautifulSoup
import logging

def setup_logging(target_folder):
    # Set up logging configuration
    log_file = os.path.join(target_folder, "missing_keyrefs_log.txt")
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

def read_keydefs(keydef_folder):
    key_href_mapping = {}
    # Iterate through files in the keydef folder
    for filename in os.listdir(keydef_folder):
        if filename.endswith('.ditamap'):
            filepath = os.path.join(keydef_folder, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'xml')
                keydefs = soup.find_all('keydef')
                for keydef in keydefs:
                    key = keydef.get('keys')
                    href = keydef.get('href')
                    if key and href:
                        key_href_mapping[key] = href
    return key_href_mapping

def process_dita_files(source_folder, target_folder, key_href_mapping):
    total_keyrefs = 0
    missing_keyrefs = []

    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.endswith('.dita'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                soup = BeautifulSoup(content, 'xml')
                images = soup.find_all('image')
                
                for image in images:
                    keyref = image.get('keyref')
                    if keyref:
                        total_keyrefs += 1
                        if keyref in key_href_mapping:
                            image['href'] = key_href_mapping[keyref]
                            del image['keyref']  # Remove the keyref attribute
                        else:
                            missing_keyrefs.append(keyref)

                # Save the modified DITA file in the target folder
                target_path = os.path.join(target_folder, os.path.relpath(root, source_folder))
                os.makedirs(target_path, exist_ok=True)
                with open(os.path.join(target_path, file), 'w', encoding='utf-8') as f:
                    f.write(str(soup))

    return total_keyrefs, missing_keyrefs

def main():
    print("Starting DITA processing...")
    
    # Prompt for the document folder name
    doc_name = input("Enter the document folder name (docName): ")
    
    source_folder = os.path.join("C:\\\\_dita_source", doc_name)
    target_folder = os.path.join("C:\\\\_dita_target", doc_name)
    keydef_folder = os.path.join(source_folder, "keydef")

    # Clear existing target folder if it already exists
    if os.path.exists(target_folder):
        shutil.rmtree(target_folder)  # Remove the folder and its contents
    os.makedirs(target_folder)  # Create a new target folder

    setup_logging(target_folder)
    
    # Read key definitions from keydef maps
    key_href_mapping = read_keydefs(keydef_folder)

    # Process DITA files and replace keyrefs
    total_keyrefs, missing_keyrefs = process_dita_files(source_folder, target_folder, key_href_mapping)

    # Logging results for missing keyrefs
    if missing_keyrefs:
        for keyref in missing_keyrefs:
            logging.info(f'Missing key definition for keyref: {keyref}')

    # Final print messages
    print(f'Operation complete: Found {total_keyrefs} keyrefs.')

    # Count of missing keyrefs
    missing_count = len(missing_keyrefs)
    
    if missing_count > 0:
        print(f'Found {missing_count} missing keyrefs, logged to {os.path.join(target_folder, "missing_keyrefs_log.txt")}.')
    else:
        print('No missing keyrefs found.')

if __name__ == "__main__":
    main()