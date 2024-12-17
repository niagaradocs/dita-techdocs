from bs4 import BeautifulSoup
import os
import re


def transform_toc_html_to_xml(toc_html_path, toc_xml_path):
    """
    Transform toc.html to toc.xml format.
    Ensures 'index.html' is added as the first entry if it is not already present.
    """
    if not os.path.exists(toc_html_path):
        print(f"Error: toc.html not found at {toc_html_path}.")
        return

    with open(toc_html_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    # Check for 'index.html' reference in toc
    index_found = any("index.html" in link.get("href", "") for link in soup.find_all("a"))
    if index_found:
        print("Reference to 'index.html' found in toc.html.")
    else:
        print("No reference to 'index.html' found. Adding it as the first entry in toc.xml.")

    # Generate the toc.xml file
    with open(toc_xml_path, "w", encoding="utf-8") as file:
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n<toc>\n')

        # Add 'index.html' as the first entry if not found
        if not index_found:
            file.write('  <tocitem target="index.html" text="Home" />\n')

        # Write existing items
        for item in soup.find_all("a"):
            href = item.get("href", "")
            text = item.text.strip()
            file.write(f'  <tocitem target="{href}" text="{text}" />\n')

        file.write("</toc>\n")
        print("toc.xml created successfully with 'index.html' as the first entry (if not already present).")

    os.remove(toc_html_path)
    print("toc.html has been deleted after conversion.")


def format_html(content):
    """
    Ensures specific HTML tags start on a new line for improved readability.
    Handles tags with attributes as well.
    """
    tags_to_format = ["head", "title", "body", "div"]

    # Create a regex pattern to match opening and closing tags, with optional attributes
    tag_pattern = r"(<(/?)(%s)([^>]*)>)" % "|".join(tags_to_format)

    def add_newline(match):
        # Add a newline before the matched tag
        tag = match.group(0)
        return f"\n{tag}"

    # Use regex to find and format the tags
    content = re.sub(tag_pattern, add_newline, content, flags=re.IGNORECASE)

    return content
