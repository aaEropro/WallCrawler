import sys
import zipfile
from xml.etree import ElementTree
from bs4 import BeautifulSoup
from settings import Settings
from pathlib import Path, PurePosixPath
import logging


log = logging.getLogger(__name__)


def _stylesheetParser(stylesheet: str) -> [list[str], list[str]]:
    stylesheet = stylesheet.strip()
    elements = stylesheet.split('}')
    italic_elements = list()
    bold_elements = list()

    for element in elements[:-1]:
        element = element.strip()
        parts = element.split('{')
        if len(parts) < 2:
            print(f"error, not closed: '{element}'")
            continue

        head = parts[0].strip()
        body = parts[1].strip().lower()

        if '@' in head:  # ignore at-rule
            continue

        if "italic" in body:
            italic_elements.append(head)

        if "bold" in body:
            bold_elements.append(head)

    return italic_elements, bold_elements


def _getClasses(epub: zipfile.ZipFile):
    italic_classes = ['i', "em"]
    bold_classes = ['b', "strong"]

    for item in epub.namelist():
        if item.endswith(".css"):
            with epub.open(item) as f:
                stylesheet = f.read().decode('utf-8')

            log.info(f"processing stylesheet {item}")
            processed_styles = _stylesheetParser(stylesheet)
            italic_classes.extend(processed_styles[0])
            bold_classes.extend(processed_styles[1])

    log.info(f"got css classes:\n> italic: {italic_classes}\n> bold: {bold_classes}")

    return [italic_classes, bold_classes]


def _replaceTag(tag, css_info: list[str], replace_with: str) -> bool:
    for item in css_info:
        blocks = item.split('.')
        recover_paragraphs = Settings().get("epub-extractor", "recover-paragraphs")
        if "class" in tag.attrs:
            if len(blocks) > 1 and tag["class"] == blocks[1]:
                tag.replace_with(f"{replace_with}{tag.get_text()}{replace_with}")
                return True
        elif tag.name == blocks[0]:
                tag.replace_with(f"{replace_with}{tag.get_text()}{replace_with}")
                return True
        elif tag.name == 'p' and recover_paragraphs:
            tag.replace_with(f"{tag.get_text()}\n")
            return True


def _processHtml(contents: str, to_replace: list[list[str]], styles: list[list[str]]) -> str:
    soup = BeautifulSoup(contents, 'xml')

    for tag in soup.find_all(True):
        if not (_replaceTag(tag, styles[0], '*') or _replaceTag(tag, styles[1], "**")):
            tag.unwrap()

    contents = str(soup)
    for item in to_replace:
        contents = contents.replace(item[0], item[1])

    return contents


def _getChapterPaths(epub: zipfile.ZipFile) -> list[PurePosixPath]:
    opf_file = None

    for file_name in epub.namelist():
        if file_name.lower().endswith(".opf"):
            opf_file = file_name
            break

    if not opf_file:
        log.error("content.opf file not found inside the EPUB file")
        sys.exit(1)

    with epub.open(opf_file) as f:
        tree = ElementTree.parse(f)

    namespaces = {  # Define namespaces (check your file's structure if necessary)
        'default': 'http://www.idpf.org/2007/opf'
    }

    root = tree.getroot()
    spine = root.find("default:spine", namespaces)
    manifest = {item.get("id"): item.get("href") for item in root.find("default:manifest", namespaces)}
    chapters = [manifest[itemref.get("idref")] for itemref in spine.findall("default:itemref", namespaces)]

    opf_dir = PurePosixPath(opf_file).parent
    chapter_paths = [PurePosixPath(opf_dir, item) for item in chapters]

    return chapter_paths


def epubExtractor(epub_path: Path):
    files_dump = dict()
    to_replace = Settings().get("cleaner-replace")
    content = str()

    epub = zipfile.ZipFile(epub_path, mode='r')

    classes = _getClasses(epub)
    chapters = _getChapterPaths(epub)

    for chapter in chapters:
        try:
            with epub.open(str(chapter)) as chapter_file:
                content: str = chapter_file.read().decode('utf-8')
        except KeyError as e:
            log.error(f"Could not open {chapter}: {e}")

        if Settings().get("epub-extractor", "recover-short-lines"):
            content = content.replace("\n\n", "&234")
            content = content.replace("\n", ' ')
            content = content.replace("&234", "\n")

        if content:
            content = _processHtml(content, to_replace, classes)
            content = content.replace("\n", "\n\n")
        else:
            log.error(f"Missing content")
            sys.exit(1)

        files_dump[chapter.stem] = content.strip()

    log.info(f"Read a total of {len(files_dump.keys())} splits")

    return files_dump
