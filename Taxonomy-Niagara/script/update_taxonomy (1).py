
import os
import pandas as pd
import json

# Define your working directory
working_directory = r'C:\repos\dita-techdocs\Taxonomy-Niagara'

# Define subdirectories
source_directory = os.path.join(working_directory, 'source')
output_directory = os.path.join(working_directory, 'output')
script_directory = os.path.join(working_directory, 'script')

# Define file paths
source_file_path = os.path.join(source_directory, 'Tridium_Taxonomy_1.xlsx')
output_file_path = os.path.join(output_directory, 'Updated_Taxonomy_Data.xlsx')
mapping_file_path = os.path.join(script_directory, 'column_mapping.json')

# Define worksheet names
taxonomy_sheet = 'Taxonomy Data'
vocabulary_sheet = 'Controlled Vocabulary'
raw_data_sheet = 'Raw Product Hierarchy Data'

# Load the column mappings from the JSON file
with open(mapping_file_path, 'r') as f:
    column_mapping = json.load(f)

# Load the raw data sheet from the Excel file
df_raw = pd.read_excel(source_file_path, sheet_name=raw_data_sheet, engine='openpyxl')

# Load the taxonomy data sheet from the Excel file
df_taxonomy = pd.read_excel(source_file_path, sheet_name=taxonomy_sheet, engine='openpyxl')

# Apply the column mappings
for source_col, target_col in column_mapping.items():
    if source_col in df_raw.columns:
        if target_col in df_taxonomy.columns:
            df_taxonomy[target_col] = df_raw[source_col]
            print(f"Overwritten column '{target_col}' with data from '{source_col}'.")
        else:
            print(f"Error: Target column '{target_col}' does not exist in the Taxonomy Data sheet.")
    else:
        print(f"Error: Source column '{source_col}' does not exist in the Raw Product Hierarchy Data sheet.")

# Load the controlled vocabulary sheet from the Excel file
df_vocabulary = pd.read_excel(source_file_path, sheet_name=vocabulary_sheet, engine='openpyxl')

# Write the updated taxonomy data and controlled vocabulary to the output Excel file
with pd.ExcelWriter(output_file_path, engine='openpyxl', mode='w') as writer:
    df_taxonomy.to_excel(writer, sheet_name=taxonomy_sheet, index=False)
    df_vocabulary.to_excel(writer, sheet_name=vocabulary_sheet, index=False)

print(f"Updated taxonomy data has been written to {output_file_path}")
