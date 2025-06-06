import os
import zipfile
import json
import csv

# 🔁 Replace this with the actual path to your JAR files
jar_directory = "C:\\niagara\\Niagara-4.15.0.131.18\\modules"

# Function to list all classes in a JAR file
def list_classes_in_jar(jar_path):
    classes = []
    with zipfile.ZipFile(jar_path, 'r') as jar:
        for entry in jar.namelist():
            if entry.endswith('.class'):
                classes.append(entry.replace('/', '.').replace('.class', ''))
    return classes

# Placeholder for Niagara-specific logic
def extract_metadata(class_name):
    # TODO: Replace this with actual logic using Niagara SDK or reflection
    metadata = {
        "class_name": class_name,
        "properties": [
            {
                "name": "exampleProperty",
                "type": "String",
                "description": "An example property",
                "allowed_values": ["value1", "value2"]
            }
        ]
    }
    return metadata

# Collect all metadata
all_metadata = []

# Scan the directory for JAR files
for jar_file in os.listdir(jar_directory):
    if jar_file.endswith('.jar'):
        jar_path = os.path.join(jar_directory, jar_file)
        classes = list_classes_in_jar(jar_path)
        for class_name in classes:
            metadata = extract_metadata(class_name)
            metadata["jar_file"] = jar_file
            all_metadata.append(metadata)

# Save to JSON
with open('properties.json', 'w') as json_file:
    json.dump(all_metadata, json_file, indent=4)

# Save to CSV
with open('properties.csv', 'w', newline='') as csv_file:
    fieldnames = ["jar_file", "class_name", "property_name", "property_type", "property_description", "allowed_values"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for metadata in all_metadata:
        for prop in metadata["properties"]:
            writer.writerow({
                "jar_file": metadata["jar_file"],
                "class_name": metadata["class_name"],
                "property_name": prop["name"],
                "property_type": prop["type"],
                "property_description": prop["description"],
                "allowed_values": ", ".join(prop["allowed_values"])
            })

print("Metadata extraction complete. Results saved to properties.json and properties.csv.")
