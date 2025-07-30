# This script lists all the PDF file names in a folder and saves them as a CSV and Excel file.

import os
import pandas as pd

# Define the folder path
# folder_path = r'C:\\path\\to\\your\\folder'  # Update this path to your folder
folder_path = r'C:\\Users\\e333758\\Honeywell\\PUBLIC Tridium Tech Docs - Release - Documents\\Release\\PDF-in_work\\4.15\\oem_distech\\BrandedPDFs'

# Initialize a list to store file names
pdf_filenames = []

# Walk through the folder
for root, dirs, files in os.walk(folder_path):
    for file in files:
        if file.endswith('.pdf'):
            # Trim the '.pdf' suffix
            filename_without_suffix = os.path.splitext(file)[0]
            pdf_filenames.append(filename_without_suffix)

# Create a DataFrame
df = pd.DataFrame(pdf_filenames, columns=['File Name'])

# Define output CSV and Excel file paths
csv_file_path = os.path.join(folder_path, 'pdf_filenames.csv')
excel_file_path = os.path.join(folder_path, 'pdf_filenames.xlsx')

# Save as CSV
df.to_csv(csv_file_path, index=False)

# Save as Excel
df.to_excel(excel_file_path, index=False)

print(f'Successfully created: {csv_file_path} and {excel_file_path}')