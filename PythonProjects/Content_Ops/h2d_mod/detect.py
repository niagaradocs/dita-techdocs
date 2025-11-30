
# detect.py — topic type detection
from typing import Set
from bs4 import BeautifulSoup, Tag
from utils import first_text

COMMAND_VERBS: Set[str] = {
    "click","select","open","choose","press","enter","type","set",
    "go","navigate","right-click","verify","check","enable","disable",
    "drag","drop","install","configure","start","stop","save","apply"
}

LIST_CLASS_HINTS = {"steps","procedure","task-steps","howto","instructions"}

TITLE_IMPERATIVE_VERBS = {
    "add","adjust","apply","build","change","configure","connect","create","delete",
    "discover","edit","enable","disable","export","import","install","launch","modify",
    "open","publish","remove","reset","restore","run","save","schedule","select",
    "set","start","stop","switch","update","upgrade","verify","view"
}

PROCEDURE_PHRASES = {
    "the following steps", "do the following", "perform the following",
    "complete the following", "use the following procedure",
    "to get started", "to begin", "to do this", "step by step"
}

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


def _procedural_evidence_score(soup: BeautifulSoup) -> int:
    """Score soft signals when no explicit procedural list exists."""
    score = 0
    body = soup.body or soup

    # Title cue
    h1 = body.find("h1")
    ttl = (h1 and " ".join(h1.stripped_strings)) or ""
    if not ttl:
        head_title = soup.find("title")
        if head_title and head_title.string:
            ttl = head_title.string.strip()
    first = (ttl.split() or [""])[0].lower().strip(" :.-")
    if first in TITLE_IMPERATIVE_VERBS:
        score += 2

    # Shortdesc cue: "To ..."
    sd = body.select_one('[class*="shortdesc"]')
    if sd:
        sdt = " ".join(sd.stripped_strings).strip().lower()
        if sdt.startswith("to "):
            score += 1

    # Procedure phrases anywhere
    body_text = " ".join(t.strip().lower() for t in body.stripped_strings)
    if any(p in body_text for p in PROCEDURE_PHRASES):
        score += 2

    # Imperative paragraphs (cap at +3)
    hits = 0
    for p in body.find_all("p"):
        txt = " ".join(p.stripped_strings).strip()
        if not txt:
            continue
        firstw = (txt.split() or [""])[0].lower().rstrip(":")
        if firstw in COMMAND_VERBS:
            hits += 1
            if hits >= 3:
                break
    score += min(hits, 3)
    return score


def detect_topic_type(soup: BeautifulSoup) -> str:
    body = soup.body or soup
    # 1) Strong signal: procedural list anywhere
    if any(looks_procedural_list(ul) for ul in body.find_all(["ul","ol"], recursive=True)):
        return "task"
    # 2) Tables => reference
    if has_data_table(soup):
        return "reference"
    # 3) Score soft signals
    return "task" if _procedural_evidence_score(soup) >= 3 else "concept"
