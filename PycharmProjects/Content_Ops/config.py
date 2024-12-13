# config.py
"""
Configuration module for processing HTML files.

Adjust the paths and options below to customize behavior.
"""
# Source folder containing zip files
source_root = "C:\\_zipfiles"
# source_root = "C:\\Users\\e333758\\Honeywell\\PUBLIC Tridium Tech Docs - Workbench_Help - Documents\\_zipfiles"

# Target base folder for processed documents
target_root = {
    "1": "c:\\_target_html",
    "2": "c:\\niagara\\techdocsdev\\docs\\{doc_folder_name}\\{doc_folder_name}-doc\\src\\doc"
}

# Predefined document list
doc_list = ['docAlarms']

# Logging options
LOGGING_LEVEL = "DEBUG"  # Options: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
LOG_FILE = "processing.log"  # Log file path

# Default processing option: 1 = '_target_html', 2 = 'techdocsdev'
option = "2"  # Change this if you want to preselect an option
