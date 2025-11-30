# build_reference.py — DITA Reference builder
from typing import List, Optional
from bs4 import BeautifulSoup
from utils import xml_escape, first_text
from harvest import concept_or_ref_fig, html_table_to_simpletable

def build_reference(soup: BeautifulSoup, topic_id: str, title: str,
                    graphic_rel_val: str, img_scale: Optional[str], xml_lang: str) -> str:
    body = soup.body or soup
    # reuse concept shortdesc derivation to keep parity
    from build_concept import derive_shortdesc
    shortdesc = derive_shortdesc(body)
    sections: List[str] = []

    # Tables → sections
    tables = body.find_all("table")
    for i, t in enumerate(tables, start=1):
        cap = t.find("caption")
        ttl = first_text(cap) if cap else f"Table {i}"
        st = html_table_to_simpletable(t)
        if st:
            sections.append(
                f'  <section>\n'
                f'    <title>{xml_escape(ttl)}</title>\n'
                f'{st}\n'
                f'  </section>'
            )

    # Top-level figures allowed
    for img in body.find_all("img", recursive=False):
        fig = concept_or_ref_fig(img, graphic_rel_val, img_scale)
        if fig:
            sections.append(fig)

    if not sections:
        paras = [
            f'    <p>{xml_escape(first_text(p))}</p>'
            for p in body.find_all("p") if first_text(p)
        ]
        if paras:
            sections.append(
                '  <section>\n'
                + "\n".join(paras)
                + '\n  </section>'
            )

    out: List[str] = []
    out.append('<?xml version="1.0" encoding="UTF-8"?>')
    out.append('<!DOCTYPE reference PUBLIC "-//OASIS//DTD DITA Reference//EN" "reference.dtd">')
    out.append(f'<reference id="{topic_id}" xml:lang="{xml_lang}">')
    out.append(f'  <title>{xml_escape(title)}</title>')
    out.append(f'  <shortdesc>{xml_escape(shortdesc)}</shortdesc>')
    out.append('  <refbody>')
    out.extend(sections)
    out.append('  </refbody>')
    out.append('</reference>')
    return "\n".join(out)