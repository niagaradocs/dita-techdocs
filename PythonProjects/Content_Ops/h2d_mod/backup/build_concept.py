# build_concept.py — DITA Concept builder and shared shortdesc
from typing import List, Optional
from bs4 import BeautifulSoup, Tag
from utils import xml_escape, first_text
from harvest import gather_blocks, gather_until_next_heading

def derive_shortdesc(body: Tag) -> str:
    x = body.select_one('[class*="shortdesc"]')
    if x:
        return first_text(x)
    for p in body.find_all("p"):
        txt = first_text(p)
        if txt and "Index Prev Next" not in txt and len(txt) >= 15:
            return txt
    for h in body.find_all(["h2", "h3", "h4", "h5", "h6"]):
        txt = first_text(h)
        if txt and len(txt) >= 15:
            return txt
    return ""

def build_concept(
    soup: BeautifulSoup,
    topic_id: str,
    title: str,
    graphic_rel_val: str,
    img_scale: Optional[str],
    xml_lang: str
) -> str:
    body = soup.body or soup
    shortdesc = derive_shortdesc(body)
    sections: List[str] = []
    heading_names = {"h2", "h3", "h4", "h5"}

    # Heading-based sections
    for h in body.find_all(list(heading_names)):
        st = first_text(h)
        if not st:
            continue
        blocks = gather_until_next_heading(h, heading_names, graphic_rel_val, img_scale)
        if blocks:
            sections.append(
                '  <section>\n'
                + f'    <title>{xml_escape(st)}</title>\n'
                + "\n".join(blocks)
                + "\n  </section>"
            )
        else:
            sections.append(
                '  <section>\n'
                + f'    <title>{xml_escape(st)}</title>\n'
                + '    <p/>\n'
                + '  </section>'
            )

    blocks = gather_blocks(body, graphic_rel_val, img_scale, allow_sections=True)
    if blocks:
        sections.append(
            '  <section>\n'
            + "\n".join(blocks)
            + '\n  </section>'
        )

    out: List[str] = []
    out.append('<?xml version="1.0" encoding="UTF-8"?>')
    out.append('<!DOCTYPE concept PUBLIC "-//OASIS//DTD DITA Concept//EN" "concept.dtd">')
    out.append(f'<concept id="{topic_id}" xml:lang="{xml_lang}">')
    out.append(f'  <title>{xml_escape(title)}</title>')
    out.append(f'  <shortdesc>{xml_escape(shortdesc)}</shortdesc>')
    out.append('  <conbody>')
    out.extend(sections)
    out.append('  </conbody>')
    out.append('</concept>')
    return "\n".join(out)
