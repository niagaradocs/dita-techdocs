# harvest.py — content harvesting helpers (concept/ref reuse)
from typing import List, Optional
from bs4 import BeautifulSoup, Tag, NavigableString
from utils import xml_escape, first_text
from images import best_img_src, normalize_graphic_href, image_element

# simple list mapper shared by concept/ref
def to_simplelist(ul: Tag) -> str:
    items = "".join(
        f"    <li>{xml_escape(first_text(li))}</li>\n"
        for li in ul.find_all("li", recursive=False)
    )
    if not items:
        return ""
    return f"<ul>\n{items}</ul>"

def concept_or_ref_fig(img_tag: Tag, graphic_rel_val: str, img_scale: Optional[str]) -> str:
    src = best_img_src(img_tag)
    if not src:
        return ""
    href = normalize_graphic_href(src, graphic_rel_val)
    return f"""  <fig>
    {image_element(href, placement='break', scale=img_scale)}
  </fig>"""

def html_table_to_simpletable(tbl: Tag) -> str:
    rows = tbl.find_all("tr")
    if not rows:
        return ""
    has_th = bool(tbl.find("th"))
    out: List[str] = []
    if has_th:
        hdr = next((r for r in rows if r.find("th")), None)
        if hdr:
            out.append("<simpletable>")
            out.append("  <sthead>")
            out.append("    <strow>")
            for th in hdr.find_all(["th", "td"]):
                out.append(f"      <stentry>{xml_escape(first_text(th))}</stentry>")
            out.append("    </strow>")
            out.append("  </sthead>")
        for r in rows:
            if has_th and r.find("th"):
                continue
            cells = r.find_all(["td", "th"])
            if not cells:
                continue
            out.append("  <strow>")
            for td in cells:
                out.append(f"    <stentry>{xml_escape(first_text(td))}</stentry>")
            out.append("  </strow>")
        out.append("</simpletable>")
    else:
        out.append("<simpletable>")
        for r in rows:
            cells = r.find_all(["td", "th"])
            if not cells:
                continue
            out.append("  <strow>")
            for td in cells:
                out.append(f"    <stentry>{xml_escape(first_text(td))}</stentry>")
            out.append("  </strow>")
        out.append("</simpletable>")
    return "\n".join(out)

def _gather_concept_blocks(container: Tag, graphic_rel_val: str, img_scale: Optional[str], allow_sections: bool = False) -> List[str]:
    """
    Collect <p>, lists, images (<img>), tables (<table>), and handle orphan <li> blocks by wrapping consecutive <li> into a <ul>.
    Preserve order; recurse into wrappers.
    """
    blocks: List[str] = []
    children = [ch for ch in container.children if isinstance(ch, (Tag, NavigableString))]
    i = 0
    while i < len(children):
        node = children[i]
        if isinstance(node, NavigableString):
            i += 1
            continue
        name = (node.name or "").lower()
        # Orphan <li> → synthetic <ul>
        if name == "li":
            li_items = []
            j = i
            while j < len(children) and isinstance(children[j], Tag) and (children[j].name or "").lower() == "li":
                li_items.append(children[j])
                j += 1
            if li_items:
                # Defensive: ensure container is not None and has new_tag
                if container is not None and hasattr(container, "new_tag"):
                    fake_ul = container.new_tag("ul")
                    for li in li_items:
                        fake_ul.append(li)
                    lst = to_simplelist(fake_ul)
                    if lst:
                        blocks.append(lst)
                else:
                    # If container is None, skip or handle gracefully
                    print("Warning: container is None or does not support new_tag. Skipping orphan <li> wrap.")
            i = j
            continue
        if name == "p":
            txt = xml_escape(first_text(node)).strip()
            # label + list detection
            if txt.endswith(":"):
                j = i + 1
                while j < len(children) and isinstance(children[j], NavigableString):
                    j += 1
                if j < len(children) and isinstance(children[j], Tag) and (children[j].name or "").lower() in {"ul", "ol"}:
                    label = txt[:-1].strip()
                    lst_xml = to_simplelist(children[j])
                    if lst_xml:
                        if allow_sections:
                            blocks.append(f"<section>\n  <title>{label}</title>\n{lst_xml}\n</section>")
                        else:
                            blocks.append(f"<p><b>{label}</b></p>")
                            blocks.append(lst_xml)
                    i = j + 1
                    continue
            if txt:
                blocks.append(f"<p>{txt}</p>")
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

def _gather_until_next_heading(start: Tag, heading_names: set, graphic_rel_val: str, img_scale: Optional[str]) -> List[str]:
    blocks: List[str] = []
    sib = start.next_sibling
    from bs4 import Tag as _Tag
    while sib:
        if isinstance(sib, _Tag) and (sib.name or "").lower() in heading_names:
            break
        if isinstance(sib, _Tag):
            # special: label + list across siblings
            name = (sib.name or '').lower()
            if name == 'p':
                txt = xml_escape(first_text(sib)).strip()
                if txt.endswith(':'):
                    nxt = sib.next_sibling
                    while nxt is not None and not isinstance(nxt, _Tag):
                        nxt = nxt.next_sibling
                    if isinstance(nxt, _Tag) and (nxt.name or '').lower() in {'ul', 'ol'}:
                        label = txt[:-1].strip()
                        from harvest import to_simplelist as _tsl  # safe local import
                        lst_xml = _tsl(nxt)
                        if lst_xml:
                            blocks.append(f"<p><b>{label}</b></p>")
                            blocks.append(lst_xml)
                        sib = nxt.next_sibling
                        continue
            blocks.extend(_gather_concept_blocks(sib, graphic_rel_val, img_scale, allow_sections=False))
        sib = sib.next_sibling
    return blocks

# public helpers for builders
def gather_blocks(container: Tag, graphic_rel_val: str, img_scale: Optional[str], allow_sections: bool=False) -> List[str]:
    return _gather_concept_blocks(container, graphic_rel_val, img_scale, allow_sections)

def gather_until_next_heading(start: Tag, heading_names: set, graphic_rel_val: str, img_scale: Optional[str]) -> List[str]:
    return _gather_until_next_heading(start, heading_names, graphic_rel_val, img_scale)