
import pandas as pd

# Load the taxonomy data
taxonomy_data = pd.read_excel('Tridium_Taxonomy_Data_Clean_IDs.xlsx', sheet_name='Taxonomy Data', engine='openpyxl')

# Load the controlled vocabulary
controlled_vocabulary = pd.read_excel('Tridium_Taxonomy_Data_Clean_IDs.xlsx', sheet_name='Controlled Vocabulary', engine='openpyxl')

# Load the raw product hierarchy data
raw_data = pd.read_excel('Tridium_Taxonomy_Data_Clean_IDs.xlsx', sheet_name='Raw Product Hierarchy Data', engine='openpyxl')

# Hardcoded column mapping
column_mapping = {
    "Material Name": "Preferred Term",
    "Material Number": "Tridium Part No.",
    "PH3 - Prod. Family": "Parent Term",
    "PH4 - Prod. Line": "Tag Type",
    "PH6 - Prod. Model": "Synonyms",
}

# Initialize log file
log = []

# Initialize ID counter
id_counter = 66  # Assuming the last ID in the taxonomy data is TX-0065

# List of existing Preferred Terms
existing_terms = taxonomy_data['Preferred Term'].dropna().tolist()

# List of existing IDs
existing_ids = taxonomy_data['ID'].dropna().tolist()

# Controlled vocabulary values
controlled_vocab_values = controlled_vocabulary.set_index('Tag Category')['Allowed Value'].to_dict()

# Function to validate metadata fields
def validate_metadata(field, value):
    if field in controlled_vocab_values and str(value) not in controlled_vocab_values[field]:
        return False
    return True

# Process each row in the raw product hierarchy data
for index, row in raw_data.iterrows():
    new_entry = {}
    validation_notes = []

    # Map source columns to taxonomy fields
    for source_col, taxonomy_field in column_mapping.items():
        new_entry[taxonomy_field] = row[source_col]

    # Check for duplicate Preferred Term
    if new_entry['Preferred Term'] in existing_terms:
        log.append(f"[WARNING] Skipped duplicate: {new_entry['Preferred Term']}")
        continue

    # Validate metadata fields
    for field, value in new_entry.items():
        if not validate_metadata(field, value):
            validation_notes.append(f"Invalid value for {field}: {value}")
            log.append(f"[WARNING] Invalid value for {field}: {value}")

    # Validate Parent Term
    if new_entry['Parent Term'] not in existing_terms:
        new_entry['Parent Term'] = 'Uncategorized'
        validation_notes.append("Parent Term not found. Assigned 'Uncategorized'")
        log.append(f"[INFO] Assigned fallback parent 'Uncategorized' to entry: {new_entry['Preferred Term']}")

    # Generate new unique ID
    new_entry['ID'] = f"TX-{id_counter:04d}"
    id_counter += 1

    # Add validation notes
    new_entry['Validation Notes'] = "; ".join(validation_notes)

    # Append new entry to taxonomy data
    taxonomy_data = pd.concat([taxonomy_data, pd.DataFrame([new_entry])], ignore_index=True)

    # Log the addition
    log.append(f"[INFO] Added: {new_entry['ID']} - {new_entry['Preferred Term']}")

# Save the updated taxonomy data to a new Excel file
taxonomy_data.to_excel('Updated_Taxonomy_Data.xlsx', index=False, engine='openpyxl')

# Save the log file
with open('update_log.txt', 'w') as f:
    f.write("\n".join(log))
