#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML → DITA (Task | Concept | Reference) — Tridium/Heretto tuned

Integrated fixes:
  • Robust concept harvesting (handles wrapper <div>/<section> and heading-only pages)
  • Broadened heading detection (H2–H5)
  • Fallback collects all paragraphs/lists/images anywhere in body
  • “Label + list” pattern handling (e.g., "Controllers:" followed by <ul>)
  • Shortdesc fallback to first meaningful sub-heading when no paragraph exists
  • Correct <image/> emission
  • DITA DOCTYPE declarations for task/concept/reference
"""

import shutil
import re
from pathlib import Path
from typing import List, Optional, Tuple
from bs4 import BeautifulSoup, Tag, NavigableString

# ----------------------- USER SETTINGS -----------------------
input_folder = r"C:\\Users\\e333758\\Honeywell\\PUBLIC Tridium Tech Docs - Release - Documents\\Release\\PDF-in_work\\ProfessionalServices\\html_input"
output_folder = r"C:\\Users\\e333758\\Honeywell\\PUBLIC Tridium Tech Docs - Release - Documents\\Release\\PDF-in_work\\ProfessionalServices\\xml_output"

# CCMS path used INSIDE DITA hrefs (not the filesystem copy target)
# Use "graphic" when topics and /graphic live side-by-side at import time (your case).
graphic_rel = "graphic"
image_scale = "65"           # "" to omit scale on block images
topic_type = "auto"          # "auto" | "task" | "concept" | "reference"
xml_lang = "en-us"

# Copy control: copy /graphics → /graphic
copy_graphics = True
source_graphics_name = "graphics"  # name in the input folder
target_graphics_name = "graphic"   # name to create under the output folder

# ----------------------- Heuristics --------------------------
COMMAND_VERBS = {
    "click","select","open","choose","press","enter","type","set",
    "go","navigate","right-click","verify","check","enable","disable",
    "drag","drop","install","configure","start","stop","save","apply"
}
LIST_CLASS_HINTS = {"steps","procedure","task-steps","howto","instructions"}
ICON_HINTS = ("icon", "ic_")

# ----------------------- Utility helpers ---------------------

def slug(text: str) -> str:
    s = re.sub(r"[^A-Za-z0-9_.-]+", "_", (text or "").strip())
    return s.strip("_") or "topic"

def sanitize(text: str) -> str:
    if text is None:
        return ""
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
    )

def first_text(node: Optional[Tag]) -> str:
    if not node:
        return ""
    return " ".join(t.strip() for t in node.stripped_strings)

def get_doc_title(soup: BeautifulSoup, default_stem: str) -> str:
    head_title = soup.find("title")
    if head_title and head_title.string:
        t = head_title.string.strip()
        if t:
            return t
    h = soup.find(["h1","h2"])
    if h:
        t = first_text(h)
        if t:
            return t
    return default_stem

def strip_boilerplate(soup: BeautifulSoup):
    for sel in [
        "head", "nav", "footer", "script", "style",
        "aside[role='navigation']", "p.navbar", "[class*='navbar']", "p.copyright"
    ]:
        for n in soup.select(sel):
            n.decompose()

def looks_procedural_list(ul: Tag) -> bool:
    cls = set(ul.get("class") or [])
    if cls & LIST_CLASS_HINTS:
        return True
    for li in ul.find_all("li", recursive=False):
        if li.select_one(".x-stepresult"):
            return True
        lead = (first_text(li).split() or [""])[0].lower().rstrip(":")
        if lead in COMMAND_VERBS:
            return True
    return False

def has_data_table(soup: BeautifulSoup) -> bool:
    return bool(soup.find("table"))

def detect_topic_type(soup: BeautifulSoup) -> str:
    body = soup.body or soup
    if any(looks_procedural_list(ul) for ul in body.find_all(["ul","ol"], recursive=True)):
        return "task"
    if has_data_table(soup):
        return "reference"
    return "concept"

# ----------------------- Shortdesc ---------------------------

def derive_shortdesc(body: Tag) -> str:
    x = body.select_one('[class*="shortdesc"]')
    if x:
        return first_text(x)
    for p in body.find_all("p"):
        txt = first_text(p)
        if txt and "Index \n Prev \n Next" not in txt and len(txt) >= 15:
            return txt
    for h in body.find_all(["h2", "h3", "h4", "h5", "h6"]):
        txt = first_text(h)
        if txt and len(txt) >= 15:
            return txt
    return ""

# ----------------------- Images ------------------------------

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
    """
    Return a proper DITA <image> element with explicit closing tag, e.g.:
      graphic/pic.png</image>
    """
    # Build attributes on the opening tag
    parts = [f'href="{sanitize(href)}"']
    if placement:
        parts.append(f'placement="{placement}"')
    if scale:
        parts.append(f'scale="{scale}"')
    return f'<image {" ".join(parts)}></image>'

# ----------------------- Task-specific helpers ---------------

def extract_cmd_with_inline_icons(li: Tag, graphic_rel_val: str) -> str:
    parts: List[str] = []
    for node in li.contents:
        if isinstance(node, NavigableString):
            if node.strip():
                parts.append(sanitize(str(node)))
        elif isinstance(node, Tag):
            if node.name == "img" and is_icon(node):
                src = best_img_src(node)
                if src:
                    href = normalize_graphic_href(src, graphic_rel_val)
                    parts.append(image_element(href, placement="inline"))
            elif node.name in {"span","b","strong","i","em","u","code","kbd","samp"}:
                parts.append(sanitize(first_text(node)))
            elif "x-stepresult" in (node.get("class") or []):
                continue
            else:
                parts.append(sanitize(first_text(node)))
    cmd_text = " ".join(p for p in parts if p).strip() or "Perform the step."
    return cmd_text

def collect_non_icon_step_imgs(li: Tag) -> List[str]:
    imgs: List[str] = []
    for img in li.find_all("img"):
        if not is_icon(img):
            src = best_img_src(img)
            if src:
                imgs.append(src)
    return imgs

def nearest_intro_para_for_list(first_list: Tag) -> Optional[Tag]:
    container = first_list.parent
    for _ in range(3):
        if not container or container.name == "body":
            break
        prev_p: Optional[Tag] = None
        for child in container.children:
            if child is first_list:
                break
            if isinstance(child, Tag) and child.name == "p":
                t = first_text(child)
                if t and "Index \n Prev \n Next" not in t:
                    prev_p = child
        if prev_p:
            return prev_p
        container = container.parent
    return None

# ----------------------- Builders: TASK ----------------------

def build_task(soup: BeautifulSoup, topic_id: str, title: str,
               graphic_rel_val: str, img_scale: Optional[str]) -> str:
    body = soup.body or soup
    shortdesc = derive_shortdesc(body)

    proc_lists = [ul for ul in body.find_all(["ul","ol"], recursive=True) if looks_procedural_list(ul)]
    steps_blocks: List[str] = []

    context_xml = ""
    if proc_lists:
        intro = nearest_intro_para_for_list(proc_lists[0])
        if intro:
            ctx = sanitize(first_text(intro))
            if ctx:
                context_xml = f"    <context>{ctx}</context>"

    if not proc_lists:
        p = body.find("p")
        cmd = sanitize(first_text(p)) or "Perform the task."
        steps_blocks.append(
            "    <steps>\n"
            "      <step>\n"
            f"        <cmd>{cmd}</cmd>\n"
            "      </step>\n"
            "    </steps>"
        )
    else:
        for ul in proc_lists:
            lis = ul.find_all("li", recursive=False)
            if not lis:
                continue
            block: List[str] = ["    <steps>"]
            for li in lis:
                cmd_text = extract_cmd_with_inline_icons(li, graphic_rel_val)
                block.append("      <step>")
                block.append(f"        <cmd>{cmd_text}</cmd>")

                step_imgs_xml: List[str] = []
                for src in collect_non_icon_step_imgs(li):
                    href = normalize_graphic_href(src, graphic_rel_val)
                    step_imgs_xml.append(image_element(href, placement="break", scale=img_scale))

                sr_node = li.select_one(".x-stepresult")
                sr_text = sanitize(first_text(sr_node)) if sr_node else ""

                if sr_text:
                    content = sr_text + (" " if sr_text and step_imgs_xml else "")
                    content += "".join(step_imgs_xml)
                    block.append(f"        <stepresult>{content}</stepresult>")
                elif step_imgs_xml:
                    block.append("        <info>")
                    for img_xml in step_imgs_xml:
                        block.append(f"          {img_xml}")
                    block.append("        </info>")

                block.append("      </step>")
            block.append("    </steps>")
            steps_blocks.append("\n".join(block))

    out: List[str] = []
    out.append('<?xml version="1.0" encoding="UTF-8"?>')
    out.append('<!DOCTYPE task PUBLIC "-//OASIS//DTD DITA Task//EN" "task.dtd">')
    out.append(f'<task id="{topic_id}" xml:lang="{xml_lang}">')
    out.append(f'  <title>{sanitize(title)}</title>')
    out.append(f'  <shortdesc>{sanitize(shortdesc)}</shortdesc>')
    out.append('  <taskbody>')
    if context_xml:
        out.append(context_xml)
    out.extend(steps_blocks)
    out.append('  </taskbody>')
    out.append('</task>')
    return "\n".join(out)

# ----------------------- List mapping ------------------------

def to_simplelist(ul: Tag) -> str:
    items = "".join(f"    <li>{sanitize(first_text(li))}</li>\n" for li in ul.find_all("li", recursive=False))
    if not items:
        return ""
    return f"  <ul>\n{items}  </ul>"

# ----------------------- Concept/Ref helpers -----------------

def concept_or_ref_fig(img_tag: Tag, graphic_rel_val: str, img_scale: Optional[str]) -> str:
    src = best_img_src(img_tag)
    if not src:
        return ""
    href = normalize_graphic_href(src, graphic_rel_val)
    return f"  <fig>\n    {image_element(href, placement='break', scale=img_scale)}\n  </fig>"

def html_table_to_simpletable(tbl: Tag) -> str:
    rows = tbl.find_all("tr")
    if not rows:
        return ""
    has_th = bool(tbl.find("th"))
    out: List[str] = ['  <simpletable>']
    if has_th:
        hdr = next((r for r in rows if r.find("th")), None)
        if hdr:
            out.append('    <sthead>')
            out.append('      <strow>')
            for th in hdr.find_all(["th","td"]):
                out.append(f"        <stentry>{sanitize(first_text(th))}</stentry>")
            out.append('      </strow>')
            out.append('    </sthead>')
    for r in rows:
        if has_th and r.find("th"):
            continue
        cells = r.find_all(["td","th"])
        if not cells:
            continue
        out.append('    <strow>')
        for td in cells:
            out.append(f"      <stentry>{sanitize(first_text(td))}</stentry>")
        out.append('    </strow>')
    out.append('  </simpletable>')
    return "\n".join(out)

# ----------------------- Concept harvesting ------------------

def _gather_concept_blocks(container: Tag,
                           graphic_rel_val: str,
                           img_scale: Optional[str],
                           allow_sections: bool = False) -> List[str]:
    blocks: List[str] = []
    children = [ch for ch in container.children if isinstance(ch, (Tag, NavigableString))]
    i = 0
    while i < len(children):
        node = children[i]
        if isinstance(node, NavigableString):
            i += 1
            continue
        name = (node.name or "").lower()

        if name == "p":
            txt = sanitize(first_text(node)).strip()
            if txt.endswith(":"):
                j = i + 1
                while j < len(children) and isinstance(children[j], NavigableString):
                    j += 1
                if j < len(children) and isinstance(children[j], Tag) and (children[j].name or "").lower() in {"ul", "ol"}:
                    label = txt[:-1].strip()
                    lst_xml = to_simplelist(children[j])
                    if lst_xml:
                        if allow_sections:
                            blocks.append(
                                f"  <section>\n"
                                f"    <title>{label}</title>\n"
                                f"{lst_xml}\n"
                                f"  </section>"
                            )
                        else:
                            blocks.append(f"  <p><b>{label}</b></p>")
                            blocks.append(lst_xml)
                        i = j + 1
                        continue
            if txt:
                blocks.append(f"  <p>{txt}</p>")
            i += 1
            continue

        elif name in {"ul", "ol"}:
            lst = to_simplelist(node)
            if lst:
                blocks.append(lst)
            i += 1
            continue

        elif name == "img":
            fig = concept_or_ref_fig(node, graphic_rel_val, img_scale)
            if fig:
                blocks.append(fig)
            i += 1
            continue

        elif name == "table":
            st = html_table_to_simpletable(node)
            if st:
                blocks.append(st)
            i += 1
            continue

        elif name in {"script", "style", "nav", "footer", "head"}:
            i += 1
            continue

        else:
            blocks.extend(_gather_concept_blocks(node, graphic_rel_val, img_scale, allow_sections))
            i += 1

    return blocks

def _gather_until_next_heading(start: Tag,
                               heading_names: set,
                               graphic_rel_val: str,
                               img_scale: Optional[str]) -> List[str]:
    blocks: List[str] = []
    sib = start.next_sibling
    while sib:
        if isinstance(sib, Tag) and (sib.name or "").lower() in heading_names:
            break
        if isinstance(sib, Tag):
            name = (sib.name or '').lower()
            if name == 'p':
                txt = sanitize(first_text(sib)).strip()
                if txt.endswith(':'):
                    nxt = sib.next_sibling
                    while nxt is not None and not isinstance(nxt, Tag):
                        nxt = nxt.next_sibling
                    if isinstance(nxt, Tag) and (nxt.name or '').lower() in {'ul','ol'}:
                        label = txt[:-1].strip()
                        lst_xml = to_simplelist(nxt)
                        if lst_xml:
                            blocks.append(f"  <p><b>{label}</b></p>")
                            blocks.append(lst_xml)
                            sib = nxt.next_sibling
                            continue
            blocks.extend(_gather_concept_blocks(sib, graphic_rel_val, img_scale, allow_sections=False))
        sib = sib.next_sibling
    return blocks

# ----------------------- Builders: CONCEPT -------------------

def build_concept(soup: BeautifulSoup, topic_id: str, title: str,
                  graphic_rel_val: str, img_scale: Optional[str]) -> str:
    body = soup.body or soup
    shortdesc = derive_shortdesc(body)

    sections: List[str] = []
    heading_names = {"h2", "h3", "h4", "h5"}

    for h in body.find_all(list(heading_names)):
        st = first_text(h)
        if not st:
            continue
        blocks = _gather_until_next_heading(h, heading_names, graphic_rel_val, img_scale)
        if blocks:
            sections.append(
                '  <section>\n' +
                f'    <title>{sanitize(st)}</title>\n' +
                "\n".join(blocks) + "\n" +
                '  </section>'
            )
        else:
            sections.append(
                '  <section>\n' +
                f'    <title>{sanitize(st)}</title>\n' +
                '    <p/>\n' +
                '  </section>'
            )

    if not sections:
        blocks = _gather_concept_blocks(body, graphic_rel_val, img_scale, allow_sections=True)
        if blocks:
            sections.append('  <section>\n' + "\n".join(blocks) + '\n  </section>')

    out: List[str] = []
    out.append('<?xml version="1.0" encoding="UTF-8"?>')
    out.append('<!DOCTYPE concept PUBLIC "-//OASIS//DTD DITA Concept//EN" "concept.dtd">')
    out.append(f'<concept id="{topic_id}" xml:lang="{xml_lang}">')
    out.append(f'  <title>{sanitize(title)}</title>')
    out.append(f'  <shortdesc>{sanitize(shortdesc)}</shortdesc>')
    out.append('  <conbody>')
    out.extend(sections)
    out.append('  </conbody>')
    out.append('</concept>')
    return "\n".join(out)

# ----------------------- Builders: REFERENCE -----------------

def build_reference(soup: BeautifulSoup, topic_id: str, title: str,
                    graphic_rel_val: str, img_scale: Optional[str]) -> str:
    body = soup.body or soup
    shortdesc = derive_shortdesc(body)

    sections: List[str] = []

    tables = body.find_all("table")
    for i, t in enumerate(tables, start=1):
        cap = t.find("caption")
        ttl = first_text(cap) if cap else f"Table {i}"
        st = html_table_to_simpletable(t)
        if st:
            sections.append(
                f"  <section>\n    <title>{sanitize(ttl)}</title>\n{st}\n  </section>"
            )

    for img in body.find_all("img", recursive=False):
        fig = concept_or_ref_fig(img, graphic_rel_val, img_scale)
        if fig:
            sections.append(fig)

    if not sections:
        paras = [f"  <p>{sanitize(first_text(p))}</p>" for p in body.find_all("p") if first_text(p)]
        if paras:
            sections.append('  <section>\n' + "\n".join(paras) + '\n  </section>')

    out: List[str] = []
    out.append('<?xml version="1.0" encoding="UTF-8"?>')
    out.append('<!DOCTYPE reference PUBLIC "-//OASIS//DTD DITA Reference//EN" "reference.dtd">')
    out.append(f'<reference id="{topic_id}" xml:lang="{xml_lang}">')
    out.append(f'  <title>{sanitize(title)}</title>')
    out.append(f'  <shortdesc>{sanitize(shortdesc)}</shortdesc>')
    out.append('  <refbody>')
    out.extend(sections)
    out.append('  </refbody>')
    out.append('</reference>')
    return "\n".join(out)

# ----------------------- Driver ------------------------------

def convert_one(html_path: Path, out_dir: Path, force_type: str,
                graphic_rel_val: str, img_scale: Optional[str]) -> Tuple[Path, str]:
    src = html_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(src, "lxml")

    title = get_doc_title(soup, default_stem=html_path.stem)
    strip_boilerplate(soup)

    topic_id = slug(html_path.stem)
    ttype = force_type if force_type != "auto" else detect_topic_type(soup)

    if ttype == "task":
        xml = build_task(soup, topic_id, title, graphic_rel_val, img_scale or None)
    elif ttype == "reference":
        xml = build_reference(soup, topic_id, title, graphic_rel_val, img_scale or None)
    else:
        xml = build_concept(soup, topic_id, title, graphic_rel_val, img_scale or None)

    out = out_dir / f"{html_path.stem}.dita"
    out.write_text(xml, encoding="utf-8")
    return out, ttype

def copy_graphics_tree(src_root: Path, dst_root: Path,
                       src_name: str = "graphics", dst_name: str = "graphic") -> None:
    src = src_root / src_name
    if not src.exists() or not src.is_dir():
        print(f"(Info) No '{src_name}' directory found under {src_root}; skipping copy.")
        return
    dst = dst_root / dst_name
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, dirs_exist_ok=True)
    print(f"✔ Copied '{src}' → '{dst}'")

def main():
    in_dir = Path(input_folder)
    out_dir = Path(output_folder)
    out_dir.mkdir(parents=True, exist_ok=True)

    if copy_graphics:
        copy_graphics_tree(in_dir, out_dir, source_graphics_name, target_graphics_name)

    htmls = sorted([p for p in in_dir.iterdir() if p.suffix.lower() in {".html",".htm"}])
    if not htmls:
        print(f"No HTML files found in {in_dir}")
        return

    for p in htmls:
        out, ttype = convert_one(p, out_dir, topic_type, graphic_rel, image_scale or None)
        print(f"✔ {p.name} → {out.name} ({ttype})")

    print(f"\nDone. Wrote {len(htmls)} topic(s) to {out_dir}")

if __name__ == "__main__":
    main()