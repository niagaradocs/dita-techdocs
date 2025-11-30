# main.py — driver
from pathlib import Path
from bs4 import BeautifulSoup

from io_paths import (input_folder, output_folder, graphic_rel, default_image_scale,
                      default_topic_type, xml_lang, copy_graphics, source_graphics_name, target_graphics_name)
from utils import slug
from stripper import strip_boilerplate
from detect import detect_topic_type
from build_task import build_task
from build_concept import build_concept
from build_reference import build_reference

import shutil


def copy_graphics_tree(src_root: Path, dst_root: Path, src_name: str = "graphics", dst_name: str = "graphic") -> None:
    src = src_root / src_name
    if not src.exists() or not src.is_dir():
        print(f"(Info) No '{src_name}' directory found under {src_root}; skipping copy.")
        return
    dst = dst_root / dst_name
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, dirs_exist_ok=True)
    print(f"✔ Copied '{src}' → '{dst}'")


def get_doc_title(soup: BeautifulSoup, default_stem: str) -> str:
    head_title = soup.find("title")
    if head_title and head_title.string:
        t = head_title.string.strip()
        if t:
            return t
    h = soup.find(["h1","h2"])
    if h:
        t = " ".join(h.stripped_strings)
        if t:
            return t
    return default_stem


def convert_one(html_path: Path, out_dir: Path,
                force_type: str, graphic_rel_val: str, img_scale: str) -> tuple[Path, str]:
    src = html_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(src, "lxml")
    title = get_doc_title(soup, default_stem=html_path.stem)
    strip_boilerplate(soup)

    topic_id = slug(html_path.stem)
    ttype = force_type if force_type != "auto" else detect_topic_type(soup)

    if ttype == "task":
        xml = build_task(soup, topic_id, title, graphic_rel_val, img_scale or None, xml_lang)
    elif ttype == "reference":
        xml = build_reference(soup, topic_id, title, graphic_rel_val, img_scale or None, xml_lang)
    else:
        xml = build_concept(soup, topic_id, title, graphic_rel_val, img_scale or None, xml_lang)

    out = out_dir / f"{html_path.stem}.dita"
    out.write_text(xml, encoding="utf-8")
    return out, ttype


def main():
    in_dir = input_folder
    out_dir = output_folder
    out_dir.mkdir(parents=True, exist_ok=True)

    if copy_graphics:
        copy_graphics_tree(in_dir, out_dir, source_graphics_name, target_graphics_name)

    htmls = sorted([p for p in in_dir.iterdir() if p.suffix.lower() in {".html",".htm"}])
    if not htmls:
        print(f"No HTML files found in {in_dir}")
        return

    for p in htmls:
        out, ttype = convert_one(p, out_dir, default_topic_type, graphic_rel, default_image_scale)
        print(f"✔ {p.name} → {out.name} ({ttype})")
    print(f"Done. Wrote {len(htmls)} topic(s) to {out_dir}")

if __name__ == "__main__":
    main()
