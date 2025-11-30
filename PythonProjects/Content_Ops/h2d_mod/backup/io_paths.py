
# io_paths.py — user-configurable paths & knobs
from pathlib import Path

# Input/output folders
input_folder  = Path(r"C:\Users\e333758\Honeywell\PUBLIC Tridium Tech Docs - Release - Documents\Release\PDF-in_work\ProfessionalServices\html_input")
output_folder = Path(r"C:\Users\e333758\Honeywell\PUBLIC Tridium Tech Docs - Release - Documents\Release\PDF-in_work\ProfessionalServices\xml_output")

# CCMS-relative folder used inside DITA hrefs (not filesystem)
# Use "graphic" when topics and /graphic live side-by-side at import (your case).
graphic_rel = "graphic"

# Image scale for block images; set to "" to omit
default_image_scale = "65"

# Auto topic detection can be overridden: "auto" | "task" | "concept" | "reference"
default_topic_type = "auto"

# xml:lang
xml_lang = "en-us"

# Copy control: copy /graphics → /graphic (no source rename)
copy_graphics = True
source_graphics_name = "graphics"
target_graphics_name = "graphic"
