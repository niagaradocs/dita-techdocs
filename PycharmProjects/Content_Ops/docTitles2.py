import os
import fitz  # PyMuPDF
import pandas as pd

# Function to extract the second line of text from the first page of a PDF
def extract_second_line_of_text(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        first_page = doc.load_page(0)
        text = first_page.get_text("text")
        lines = text.split('\n')
        if len(lines) > 1:
            return lines[1]
        else:
            return 'No second line found'
    except Exception as e:
        return f"Error: {e}"

# Folder path containing PDF files (replace with your actual path)
folder_path = 'C:\\Users\\e333758\\Honeywell\\PUBLIC Tridium Tech Docs - Release - Documents\\Release\\PDF-released\\4.15_doc-def'

# List to store file names and second lines of text
data = []

# Iterate through all files in the folder
for filename in os.listdir(folder_path):
    if filename.lower().endswith('.pdf'):
        pdf_path = os.path.join(folder_path, filename)
        second_line = extract_second_line_of_text(pdf_path)
        data.append({'File Name': filename, 'Second Line of Text': second_line})

# Create a DataFrame and save to Excel
df = pd.DataFrame(data)
output_file = 'document_titles.xlsx'
df.to_excel(output_file, index=False)

print(f"Document titles have been successfully saved to {output_file}.")
