
# utils.py — common helpers
import re
from typing import Optional
from bs4 import Tag

def slug(text: str) -> str:
    s = re.sub(r"[^A-Za-z0-9_.-]+", "_", (text or "").strip())
    return s.strip("_") or "topic"

def xml_escape(text: Optional[str]) -> str:
    if text is None:
        return ""
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;"))

def first_text(node: Optional[Tag]) -> str:
    if not node:
        return ""
    return " ".join(t.strip() for t in node.stripped_strings)
