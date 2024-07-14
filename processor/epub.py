from bs4 import BeautifulSoup
import os

from mailman.settings import Settings


def _replace_tags(tag, italic_classes: list, bold_classes: list, bolditalic_classes: list) -> bool:
    for item in italic_classes:
        if item in tag["class"]:
            tag.replace_with(f"*{tag.get_text()}*")
            return True

    for item in bold_classes:
        if item in tag["class"]:
            tag.replace_with(f"**{tag.get_text()}**")
            return True

    for item in bolditalic_classes:
        if item in tag["class"]:
            tag.replace_with(f"***{tag.get_text()}***")
            return True


def process_html(contents: str) -> str:
    italic_classes = Settings().get("current-stylesheet", "italic")
    bold_classes = Settings().get("current-stylesheet", "bold")
    bolditalic_classes = Settings().get("current-stylesheet", "bold-italic")

    soup = BeautifulSoup(contents, 'xml')

    for tag in soup.find_all(True):
        if "class" not in tag.attrs:
            tag.unwrap()
            continue

        replaced = _replace_tags(tag, italic_classes, bold_classes, bolditalic_classes)
        if not replaced:
            tag.unwrap()

    return str(soup)
