import os
import pandas as pd

# Define the folder path
# folder_path = r'C:\\Users\\e333758\\Honeywell\\PUBLIC Tridium Tech Docs - Mounting_Wiring - Documents\\Mounting_Wiring\\JACE-9000-QuickStart\\ko-kr\\_current\\Links'
folder_path = r'C:\\Users\\e333758\\Honeywell\\PUBLIC Tridium Tech Docs - Mounting_Wiring - Documents\\Mounting_Wiring\\JACE-9000-QuickStart\\_en-english\\_current\\Links'

# Initialize a list to store file details
file_records = []

# Walk through the folder
for root, dirs, files in os.walk(folder_path):
    for file in files:
        filename_without_suffix, extension = os.path.splitext(file)
        full_path = os.path.join(root, file)
        file_records.append({
            'File Name': filename_without_suffix,
            'Extension': extension.lower(),
            'Full Path': full_path
        })

# Create a DataFrame
df = pd.DataFrame(file_records)

# Define output CSV and Excel file paths
csv_file_path = os.path.join(folder_path, 'all_file_types.csv')
excel_file_path = os.path.join(folder_path, 'all_file_types.xlsx')

# Save as CSV
df.to_csv(csv_file_path, index=False)

# Save as Excel
df.to_excel(excel_file_path, index=False)

print(f'Successfully created: {csv_file_path} and {excel_file_path}')
