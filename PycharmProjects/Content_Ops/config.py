# config.py
"""
Configuration module for processing HTML files.

Adjust the paths and options below to customize behavior.
"""

# Source folder containing zip files
SOURCE_ROOT = "C:\\Users\\e333758\\Honeywell\\PUBLIC Tridium Tech Docs - Workbench_Help - Documents\\_zipfiles"

# Target base folder for processed documents
TARGET_ROOT = {
    "1": "c:\\_target_html",
    "2": "C:\\niagara\\techdocsdev\\docs"
}

# Predefined document list
DOC_LIST = ['docAlarms']

# Logging options
LOGGING_LEVEL = "DEBUG"  # Options: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
LOG_FILE = "processing.log"  # Log file path
