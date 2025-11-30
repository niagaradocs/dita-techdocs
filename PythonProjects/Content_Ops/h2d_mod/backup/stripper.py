
# stripper.py — safe boilerplate removal
from bs4 import BeautifulSoup, Tag

NAV_HINT = ("index", "prev", "next")

def strip_boilerplate(soup: BeautifulSoup):
    """Remove non-content AFTER title capture. Keep inline anchors.
    Drops whole nav bars but preserves inline anchors like <a class="navbar">.
    """
    # Always safe to drop
    for sel in ["head", "nav", "footer", "script", "style", "aside[role='navigation']"]:
        for n in soup.select(sel):
            n.decompose()

    def looks_navbar(tag: Tag) -> bool:
        if not isinstance(tag, Tag):
            return False
        if tag.name not in {"p", "div"}:
            return False
        cls = " ".join(tag.get("class") or []).lower()
        if "navbar" in cls:
            return True
        txt = " ".join(t.strip() for t in tag.stripped_strings).lower()
        return all(h in txt for h in NAV_HINT)

    # Remove only whole blocks that look like nav bars
    for t in list(soup.find_all(["p", "div"])):
        try:
            if looks_navbar(t):
                t.decompose()
        except Exception:
            continue
