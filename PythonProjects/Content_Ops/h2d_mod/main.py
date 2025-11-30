"""
main.py — HTML to DITA converter (enhanced CLI + logging version)
Author: Mike McGinnis / 2025
"""

from pathlib import Path
from bs4 import BeautifulSoup
import shutil
import argparse
import logging
import sys

# --- internal imports ---
from io_paths import (
    input_folder, output_folder, graphic_rel, default_image_scale,
    default_topic_type, xml_lang, copy_graphics,
    source_graphics_name, target_graphics_name
)
from utils import slug
from stripper import strip_boilerplate
from detect import detect_topic_type
from build_task import build_task
from build_concept import build_concept
from build_reference import build_reference


# ---------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------
def setup_logging(out_dir: Path, verbose: bool = False) -> logging.Logger:
    """Configure logging for console and file output."""
    log_file = out_dir / "h2d_mod.log"
    log_level = logging.DEBUG if verbose else logging.INFO

    logger = logging.getLogger("h2d_mod")
    logger.setLevel(log_level)

    # Clear any existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(log_level)
    ch_fmt = logging.Formatter("%(levelname)s: %(message)s")
    ch.setFormatter(ch_fmt)

    # File handler
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(log_level)
    fh_fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
    fh.setFormatter(fh_fmt)

    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger


# ---------------------------------------------------------------------
# File operations
# ---------------------------------------------------------------------
def copy_graphics_tree(src_root: Path, dst_root: Path, src_name: str = "graphics", dst_name: str = "graphic", log=None) -> None:
    src = src_root / src_name
    if not src.exists() or not src.is_dir():
        if log:
            log.info(f"(Info) No '{src_name}' directory found under {src_root}; skipping copy.")
        return
    dst = dst_root / dst_name
    dst.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copytree(src, dst, dirs_exist_ok=True)
        if log:
            log.info(f"✔ Copied '{src}' → '{dst}'")
    except Exception as e:
        if log:
            log.error(f"Failed to copy graphics folder: {e}")


def get_doc_title(soup: BeautifulSoup, default_stem: str) -> str:
    head_title = soup.find("title")
    if head_title and head_title.string:
        t = head_title.string.strip()
        if t:
            return t
    h = soup.find(["h1", "h2"])
    if h:
        t = " ".join(h.stripped_strings)
        if t:
            return t
    return default_stem


# ---------------------------------------------------------------------
# Core conversion
# ---------------------------------------------------------------------
def convert_one(html_path: Path, out_dir: Path, force_type: str, graphic_rel_val: str,
                img_scale: str, xml_lang: str, log: logging.Logger) -> tuple[Path, str]:
    """Convert one HTML file to a DITA XML file."""
    try:
        src = html_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        log.error(f"Failed to read {html_path}: {e}")
        return html_path, "error"

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

    out_path = out_dir / f"{html_path.stem}.dita"
    try:
        out_path.write_text(xml, encoding="utf-8")
    except Exception as e:
        log.error(f"Failed to write {out_path}: {e}")
        return html_path, "error"

    log.info(f"✔ {html_path.name} → {out_path.name} ({ttype})")
    return out_path, ttype


# ---------------------------------------------------------------------
# CLI and execution
# ---------------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert HTML files to DITA XML.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("--input", "-i", type=str, help="Source folder containing HTML files")
    parser.add_argument("--output", "-o", type=str, help="Destination folder for DITA XML")
    parser.add_argument("--type", "-t", choices=["auto", "task", "concept", "reference"], help="Force topic type")
    parser.add_argument("--scale", "-s", type=str, help="Image scale percentage (omit or empty for none)")
    parser.add_argument("--lang", "-l", type=str, help="XML language code (e.g. en-us)")
    parser.add_argument("--graphic-rel", "-g", type=str, help="DITA-relative graphic path")
    parser.add_argument("--copy-graphics", action=argparse.BooleanOptionalAction, help="Copy graphics folder")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    return parser.parse_args()


def main():
    # Parse CLI args
    args = parse_args()

    # Merge CLI overrides with io_paths defaults
    in_dir = Path(args.input) if args.input else input_folder
    out_dir = Path(args.output) if args.output else output_folder
    topic_type = args.type or default_topic_type
    img_scale = args.scale if args.scale is not None else default_image_scale
    lang = args.lang or xml_lang
    graphic_rel_val = args.graphic_rel or graphic_rel
    do_copy_graphics = args.copy_graphics if args.copy_graphics is not None else copy_graphics

    out_dir.mkdir(parents=True, exist_ok=True)
    log = setup_logging(out_dir, verbose=args.verbose)

    log.info("=== HTML → DITA Conversion Started ===")
    log.info(f"Input folder : {in_dir}")
    log.info(f"Output folder: {out_dir}")
    log.info(f"Topic type   : {topic_type}")
    log.info(f"Image scale  : {img_scale}")
    log.info(f"XML lang     : {lang}")
    log.info(f"Copy graphics: {do_copy_graphics}")
    log.info(f"Graphic rel  : {graphic_rel_val}")

    # Copy graphics if requested
    if do_copy_graphics:
        copy_graphics_tree(in_dir, out_dir, source_graphics_name, target_graphics_name, log)

    # Collect HTML files
    htmls = sorted([p for p in in_dir.iterdir() if p.suffix.lower() in {".html", ".htm"}])
    if not htmls:
        log.warning(f"No HTML files found in {in_dir}")
        return

    count = 0
    for p in htmls:
        _, ttype = convert_one(p, out_dir, topic_type, graphic_rel_val, img_scale, lang, log)
        if ttype != "error":
            count += 1

    log.info(f"Done. Wrote {count} topic(s) to {out_dir}")
    log.info("=== Conversion Completed ===")


if __name__ == "__main__":
    main()
