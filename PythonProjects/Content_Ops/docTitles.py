import os
import fitz  # PyMuPDF
import pandas as pd

# Function to extract title from PDF metadata
def extract_pdf_title(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        title = doc.metadata.get('title', 'No Title Found')
        return title
    except Exception as e:
        return f"Error: {e}"

# Folder path containing PDF files (replace with your actual path)
folder_path = 'C:\\Users\\e333758\\Honeywell\\PUBLIC Tridium Tech Docs - Release - Documents\\Release\\PDF-released\\4.15_doc-def'

# List to store file names and titles
data = []

# Iterate through all files in the folder
for filename in os.listdir(folder_path):
    if filename.lower().endswith('.pdf'):
        pdf_path = os.path.join(folder_path, filename)
        title = extract_pdf_title(pdf_path)
        data.append({'File Name': filename, 'Title': title})

# Create a DataFrame and save to Excel
df = pd.DataFrame(data)
output_file = 'document_titles.xlsx'
df.to_excel(output_file, index=False)

print(f"Document titles have been successfully saved to {output_file}.")
