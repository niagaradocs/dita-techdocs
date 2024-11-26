# html_utils.py
import re
from bs4 import BeautifulSoup

def format_html(content):
    """Ensure specific tags are on separate lines for clarity and readability."""
    content = re.sub(r'(\s*<head>)', r'\n\1\n', content)
    content = re.sub(r'(</head>)', r'\n\1\n', content)
    content = re.sub(r'(\s*<title>)', r'\n\1\n', content)
    content = re.sub(r'(</title>)', r'\n\1\n', content)
    content = re.sub(r'(\s*<body[^>]*>)', r'\n\1\n', content)
    content = re.sub(r'(</body>)', r'\n\1\n', content)
    return content

def parse_ul(ul, indent):
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
                items_xml += parse_ul(child_ul, indent + '   ')
            items_xml += f'{indent}</tocitem>\n'
    return items_xml

def transform_toc_html_to_xml(toc_html_path, toc_xml_path):
    """Convert toc.html to a formatted toc.xml and then delete toc.html."""
    if not os.path.exists(toc_html_path):
        print("toc.html not found for conversion.")
        return

    try:
        with open(toc_html_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        toc_content = '<?xml version="1.0" encoding="UTF-8"?>\n<toc>\n'
        toc_content += parse_ul(soup.find('ul'), '')
        toc_content += '</toc>'

        with open(toc_xml_path, 'w', encoding='utf-8') as file:
            file.write(toc_content)
            print("toc.xml created successfully.")

        os.remove(toc_html_path)
        print("toc.html has been deleted after conversion.")

    except Exception as e:
        print(f"An error occurred during toc.xml creation: {e}")

# Other HTML-related functions can also be added here.
