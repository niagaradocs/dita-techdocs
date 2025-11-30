# build_task.py — DITA Task builder
from typing import List, Optional
from bs4 import BeautifulSoup, Tag, NavigableString
from utils import xml_escape, first_text
from images import is_icon, best_img_src, normalize_graphic_href, image_element
from detect import looks_procedural_list

def extract_cmd_with_inline_icons(li: Tag, graphic_rel_val: str) -> str:
    parts: List[str] = []
    for node in li.contents:
        if isinstance(node, NavigableString):
            if node.strip():
                parts.append(xml_escape(str(node)))
        elif isinstance(node, Tag):
            if node.name == "img" and is_icon(node):
                src = best_img_src(node)
                if src:
                    href = normalize_graphic_href(src, graphic_rel_val)
                    parts.append(image_element(href, placement="inline"))
            elif node.name in {"span","b","strong","i","em","u","code","kbd","samp"}:
                parts.append(xml_escape(first_text(node)))
            elif "x-stepresult" in (node.get("class") or []):
                continue
            else:
                parts.append(xml_escape(first_text(node)))
    return " ".join(p for p in parts if p).strip() or "Perform the step."

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
                if t and "Index Prev Next" not in t:
                    prev_p = child
        if prev_p:
            return prev_p
        container = container.parent
    return None

def build_task(soup: BeautifulSoup, topic_id: str, title: str,
               graphic_rel_val: str, img_scale: Optional[str], xml_lang: str) -> str:
    body = soup.body or soup
    # shortdesc is derived by caller to avoid circular imports
    from build_concept import derive_shortdesc  # reuse same function
    shortdesc = derive_shortdesc(body)
    proc_lists = [ul for ul in body.find_all(["ul","ol"], recursive=True) if looks_procedural_list(ul)]
    steps_blocks: List[str] = []
    context_xml = ""  # Ensure context_xml is always defined
    if proc_lists:
        intro = nearest_intro_para_for_list(proc_lists[0])
        if intro:
            ctx = xml_escape(first_text(intro))
            if ctx:
                context_xml = f"    <context>{ctx}</context>"

    if not proc_lists:
        p = body.find("p")
        cmd = xml_escape(first_text(p)) or "Perform the task."
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
                sr_text = xml_escape(first_text(sr_node)) if sr_node else ""
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
    out.append(f'  <title>{xml_escape(title)}</title>')
    out.append(f'  <shortdesc>{xml_escape(shortdesc)}</shortdesc>')
    out.append('  <taskbody>')
    if context_xml:
        out.append(context_xml)
    out.extend(steps_blocks)
    out.append('  </taskbody>')
    out.append('</task>')
    return "\n".join(out)