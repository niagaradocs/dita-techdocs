
# images.py — image selection & element builder
from pathlib import Path
from typing import Optional
from bs4 import Tag
from utils import xml_escape

ICON_HINTS = ("icon", "ic_")

def best_img_src(img: Tag) -> Optional[str]:
    src = (img.get("src") or "").strip()
    if src:
        return src
    data_src = (img.get("data-src") or "").strip()
    if data_src:
        return data_src
    srcset = (img.get("srcset") or "").strip()
    if srcset:
        first = srcset.split(",")[0].strip().split()[0]
        if first:
            return first
    return None


def normalize_graphic_href(src: str, graphic_rel_val: str) -> str:
    filename = Path(src).name
    return f"{graphic_rel_val.rstrip('/')}/{filename}"


def is_icon(img_tag: Tag) -> bool:
    src = best_img_src(img_tag) or ""
    fname = Path(src).name.lower()
    if any(h in fname for h in ICON_HINTS):
        return True
    cls = " ".join(img_tag.get("class") or []).lower()
    return "icon" in cls


def image_element(href: str, placement: str = "break", scale: Optional[str] = None) -> str:
    """Return a proper DITA <image> element with explicit closing tag."""
    attrs = [f'href="{xml_escape(href)}"']
    if placement:
        attrs.append(f'placement="{xml_escape(placement)}"')
    if scale:
        attrs.append(f'scale="{xml_escape(scale)}"')
    return f"<image {' '.join(attrs)}></image>"
