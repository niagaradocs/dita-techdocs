#!/usr/bin/env python3
from pathlib import Path
import os
import shutil


def get_incremented_filename(base_name, directory):
    """Generate a new filename by checking and incrementing a number if a file with the same name exists."""
    stem = base_name.stem
    suffix = base_name.suffix
    new_file_name = base_name
    counter = 1

    # Gather existing file names in the specified directory
    existing_files = {f.stem for f in Path(directory).glob(f"{stem}-*.jar")}

    # Iteratively create new names until a unique one is found
    while new_file_name.stem in existing_files:
        new_file_name = f"{stem}-{counter}{suffix}"
        counter += 1

    return new_file_name


docs = ['docAwsUtils','docAlarms','docAapup']
#  docs = ['docAlarms', 'docAwsUtils', 'docBacnet', 'docContainer', 'docJ9MtgWrg', 'docMqtt']

for doc in docs:
    src = f'c:/niagara/techdocsdev/docs/{doc}/{doc}-doc/build/libs/'
    dst = f"c:/niagara/jarHolder/"

    # Ensure the destination directory exists
    os.makedirs(dst, exist_ok=True)

    # Find all jar files in the source directory
    jar_files = list(Path(src).glob(f"{doc}-doc*.jar"))

    if jar_files:
        # Get the jar file with the latest modification date
        latest_jar_file = max(jar_files, key=os.path.getmtime)

        # Prepare to target filename
        base_filename = f"{doc}-doc.jar"

        # Check for a unique filename in the source for renaming
        incremented_filename = get_incremented_filename(Path(base_filename), src)

        # Path to rename the latest jar file
        target_path = Path(src) / incremented_filename

        # Delete the existing target file if it exists
        if target_path.exists():
            target_path.unlink()  # This removes the file if it exists

        # Rename the latest jar file in the source folder to the unique name
        latest_jar_file.rename(target_path)
        print(f"Renamed {latest_jar_file.name} to {incremented_filename}")

        # Copy the renamed file to the destination, this will overwrite if it exists
        shutil.copy2(target_path, Path(dst) / base_filename)  # Overwrites if the file exists
        print(f"Copied {base_filename} to the jarHolder directory, overwriting if necessary")

    else:
        print(f"No jar files found for {doc}.")

    print("Modules processed")