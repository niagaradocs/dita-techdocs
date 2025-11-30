import os
import shutil

# === CONFIGURATION ===
source_folder = r"C:\Users\e333758\Honeywell\PUBLIC Tridium Tech Docs - Release - Documents\Release\PDF-in_work\4.15\oem_distech\reuse"
root_folder = r"C:\Users\e333758\Honeywell\PUBLIC Tridium Tech Docs - Release - Documents\Release\PDF-in_work\4.15\oem_distech"
dry_run = False  # Set to False to perform actual copy

# === SCRIPT ===
if not os.path.exists(source_folder):
    print(f"Source folder does not exist: {source_folder}")
    exit()

# Collect all 'reuse' folders under root, excluding the source folder
target_folders = []
for dirpath, dirnames, filenames in os.walk(root_folder):
    for dirname in dirnames:
        if dirname == "reuse":
            full_path = os.path.join(dirpath, dirname)
            if os.path.normpath(full_path) != os.path.normpath(source_folder):
                target_folders.append(full_path)

if not target_folders:
    print(f"No target 'reuse' folders found under {root_folder}")
    exit()

print(f"Found {len(target_folders)} target folders.")

# Copy files from source to each target folder
for target in target_folders:
    if dry_run:
        print(f"[DRY RUN] Would copy from {source_folder} to {target}")
    else:
        print(f"Copying to {target}...")
        for item in os.listdir(source_folder):
            src_path = os.path.join(source_folder, item)
            dst_path = os.path.join(target, item)
            if os.path.isfile(src_path):
                shutil.copy2(src_path, dst_path)

if dry_run:
    print("\nDry run complete. Set dry_run = False to perform the copy.")
else:
    print("\nCopy complete!")
