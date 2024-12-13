from bs4 import BeautifulSoup
import os


def transform_toc_html_to_xml(toc_html_path, toc_xml_path):
    """Transform toc.html to toc.xml format."""
    if not os.path.exists(toc_html_path):
        print(f"Error: toc.html not found at {toc_html_path}.")
        return

    with open(toc_html_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    toc_items = soup.find_all("a")
    with open(toc_xml_path, "w", encoding="utf-8") as file:
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n<toc>\n')
        for item in toc_items:
            href = item.get("href")
            text = item.text.strip()
            file.write(f'  <tocitem target="{href}" text="{text}" />\n')
        file.write("</toc>\n")
        print("toc.xml created successfully.")

    os.remove(toc_html_path)
    print("toc.html has been deleted after conversion.")