
import pandas as pd
import json

# Load the Excel file
excel_file = 'Tridium_Taxonomy_1.xlsx'
xls = pd.ExcelFile(excel_file)

# Read the three sheets
raw_product_hierarchy_data = pd.read_excel(xls, 'Raw Product Hierarchy Data', engine='openpyxl')
taxonomy_data = pd.read_excel(xls, 'Taxonomy Data', engine='openpyxl')
controlled_vocabulary = pd.read_excel(xls, 'Controlled Vocabulary', engine='openpyxl')

# Load the column mappings from the JSON file
with open('column_mapping.json', 'r') as f:
    column_mapping = json.load(f)

# Initialize a list to collect missing target columns
missing_columns = []

# Apply column mappings
for source_col, target_col in column_mapping.items():
    if target_col not in taxonomy_data.columns:
        missing_columns.append(target_col)
    else:
        taxonomy_data[target_col] = raw_product_hierarchy_data[source_col]
        print(f"Overwritten values in column '{target_col}' with values from '{source_col}'.")

# Print missing columns
if missing_columns:
    print(f"Missing target columns in 'Taxonomy Data': {missing_columns}")

# Save the updated Taxonomy Data and original Controlled Vocabulary to a new Excel file
output_file = 'Updated_Tridium_Taxonomy.xlsx'
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    taxonomy_data.to_excel(writer, sheet_name='Taxonomy Data', index=False)
    controlled_vocabulary.to_excel(writer, sheet_name='Controlled Vocabulary', index=False)

print(f"Updated data has been saved to '{output_file}'.")
