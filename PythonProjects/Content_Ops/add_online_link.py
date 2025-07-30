#  This script inserts a link to the online version of each HTML file in a specified documentation module.
#  It skips files that already contain the link to avoid duplication.

import os
from bs4 import BeautifulSoup

def insert_online_links(doc_module):
    """
    Inserts a styled HTML link to the online version of each HTML file
    in the specified doc_module directory, skipping files that already contain the link.
    """
    base_path = r"C:\niagara\techdocsdev\docs"
    module_path = os.path.join(base_path, doc_module, f"{doc_module}-doc", "src", "doc")

    if not os.path.isdir(module_path):
        print(f"Directory not found: {module_path}")
        return

    for root, _, files in os.walk(module_path):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        soup = BeautifulSoup(f, 'html.parser')

                    # Skip if the link already exists
                    if soup.find(string="View the latest version online ↗️"):
                        print(f"Link already exists in {file_path}, skipping.")
                        continue

                    # Construct the online URL
                    online_url = f"https://docs.niagara-community.com/bundle/{doc_module}/page/{file}"

                    # Create the link tag with inline styling
                    link_tag = soup.new_tag("a", href=online_url)
                    link_tag.string = "View the latest version online ↗️"
                    link_tag['style'] = "font-size: 0.6em; margin-left: 10px; text-decoration: none;"

                    # Insert the link inside the first <h1> if present, else after <body>
                    body = soup.body
                    if body:
                        h1 = body.find('h1')
                        if h1:
                            h1.append(link_tag)
                        else:
                            body.insert(0, link_tag)

                        # Save the modified HTML
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(str(soup))
                        print(f"Inserted link into {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    doc_module = input("Enter the docModule name (e.g., docJ9WiFi): ").strip()
    insert_online_links(doc_module)
