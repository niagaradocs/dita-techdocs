# This script copies files from a source directory to a target directory, deleting all files in the target directory before copying. 
# Using for copy from techdocsdev folder to Github techdocs repo. Working fine 2/8/25
import os
import shutil

def count_files_in_directory(directory):
    """ Counts total files in a given directory, including all subdirectories. """
    total_files = 0
    for root, dirs, files in os.walk(directory):
        total_files += len(files)
    return total_files

def count_root_files(directory):
    """ Counts files in the specified directory but excludes subdirectories. """
    total_files = 0
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path):
            total_files += 1
    return total_files

def count_graphics_files(directory):
    """ Counts graphic files in the specified directory. """
    graphic_files = 0
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path) and item.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            graphic_files += 1
    return graphic_files

def copy_files(doc_name):
    # Construct paths
    source_folder = f"C:\\\\niagara\\\\techdocsdev\\\\docs\\\\{doc_name}\\\\{doc_name}-doc\\\\src\\\\doc"
    target_folder = f"C:\\\\repos\\\\tridium-niagara-techdocs\\\\docs\\\\{doc_name}\\\\{doc_name}-doc\\\\src\\\\doc"
    
    # Check if source exists
    if not os.path.exists(source_folder):
        print(f"Error: Source directory '{source_folder}' does not exist.")
        return
    
    # Check if target exists, create it if not
    os.makedirs(target_folder, exist_ok=True)
    
    # Count files in the target root 'doc' folder and in 'graphics' before deletion
    total_root_files_before = count_root_files(target_folder)
    total_graphics_files_before = count_graphics_files(os.path.join(target_folder, 'graphics'))
    
    # Count total files including subfolders before deletion
    total_files_before = total_root_files_before + count_files_in_directory(os.path.join(target_folder, 'graphics'))

    # Report deletions
    print(f"{total_files_before} files deleted from {target_folder}.")
    
    # Clear the target directory and count deletions
    root_deleted_files = 0
    graphics_deleted_files = 0
    subfolder_deleted_files = {}
    
    # Remove files in the root directory
    for name in os.listdir(target_folder):
        item_path = os.path.join(target_folder, name)
        if os.path.isfile(item_path):
            root_deleted_files += 1
            os.remove(item_path)
        elif os.path.isdir(item_path):
            if name == "graphics":
                # Count graphics files in the subfolder before deletion
                graphics_deleted_files = count_graphics_files(item_path)
                # Remove the graphics directory
                shutil.rmtree(item_path)
            else:
                # Count non-graphics subdirectory files
                subfolder_files = count_files_in_directory(item_path)
                subfolder_deleted_files[item_path] = subfolder_files
                shutil.rmtree(item_path)

    # Report specific deletions
    print(f"{root_deleted_files} root doc folder files deleted (from target).")
    print(f"{graphics_deleted_files} graphics folder files deleted from the target graphics folder.")
    
    for subfolder, counts in subfolder_deleted_files.items():
        print(f"{counts} files deleted from {subfolder}.")

    # Count and copy files from the source directory after deletion
    total_copied_root_files = 0
    total_copied_graphics_files = 0

    for root, dirs, files in os.walk(source_folder):
        for file in files:
            source_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(source_file_path, source_folder)
            target_file_path = os.path.join(target_folder, relative_path)
            
            # Ensure target subdirectory exists
            os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
            shutil.copy2(source_file_path, target_file_path)

            # Count copied files from the root and graphics folder
            if os.path.dirname(source_file_path) == os.path.join(source_folder):
                total_copied_root_files += 1
            elif os.path.dirname(source_file_path) == os.path.join(source_folder, 'graphics'):
                total_copied_graphics_files += 1
    
    # Report copied files separately for root and graphics
    print(f"{total_copied_root_files} root doc folder files copied.")
    print(f"{total_copied_graphics_files} graphics folder files copied.")

# Run the function with user input
doc_name = input("Please enter the document name (docName): ")
copy_files(doc_name)