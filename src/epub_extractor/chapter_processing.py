from bs4 import BeautifulSoup

from utils import log
from epub_extractor.css_element import CSSElement
from utils.settings import Settings


def _convertCSSTags(css_tag: BeautifulSoup, italic_css_elements: list[CSSElement], bold_css_elements: list[CSSElement]) -> None:
    """
    goes through all tags inside the file and handles them.

    if the tags are found in the 2 provided CSS elements lists, they are replaced with the appropriate
    MD tags; else they are removed.

    if the tag contains a `href`, the `href` link in preserved.
    """
    css_id_str = f"{css_tag.name}.{css_tag["class"]}" if "class" in css_tag.attrs else css_tag.name
    target_css_element = CSSElement(css_id_str)

    replaces_with_str = str()
    found_href_str = str()

    if css_tag.has_attr("href"): # -> preserve `href` tags
        found_href_str += f"href='{css_tag["href"]}'"

    for element in italic_css_elements:
        if target_css_element == element:
            replaces_with_str += '*'
            break # -> make sure u do not double up the italic marker

    for element in bold_css_elements:
        if target_css_element == element:
            replaces_with_str += "**"
            break

    for tag in css_tag.find_all(True, recursive=False): # -> call recursively to get all child tags
        _convertCSSTags(tag, italic_css_elements, bold_css_elements)

    css_tag.replace_with(found_href_str + replaces_with_str + css_tag.get_text() + replaces_with_str)


def processChapter(content: str, css_elements: list[list[CSSElement]]):
    """
    processes the content of HTML chapter file.

    goes through the CSS tags and handles them.
    """
    strings_to_replace: list[list[str, str]]|None = Settings().get("epub-extractor", "cleaner-replace")

    if Settings().get("epub-extractor", "recover-short-lines"):
        log.warning("Function `recover short line` is deprecated. Please use Calibre's `HTML prettify` instead")
        content = content.replace("\n\n", "&234")
        content = content.replace("\n", ' ')
        content = content.replace("&234", "\n")

    soup: BeautifulSoup = BeautifulSoup(content, 'xml')

    for css_tag in soup.find_all(True, recursive=False): # -> process all tags
        _convertCSSTags(css_tag, *css_elements)

    content = str(soup)  # --> get content as string

    if strings_to_replace: # -> do all necessary replacements
        for item in strings_to_replace:
            content = content.replace(item[0], item[1])

    content = content.replace("\n", "\n\n")

    return content