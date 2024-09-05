import zipfile
import os
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from settings import Settings
from pathlib import Path


def _stylesheetParser(stylesheet: str) -> [list[str], list[str]]:
    stylesheet = stylesheet.strip().strip('}')
    elements = stylesheet.split('}')
    italic_elements = list()
    bold_elements = list()

    for element in elements:
        # print(element)
        element = element.strip()
        parts = element.split('{')
        if len(parts) < 2:
            print(f"error, not closed: '{element}'")
            continue

        head = parts[0].strip()
        body = parts[1].strip().lower()

        if '@' in head:  # ignore at-ule
            continue

        if "italic" in body:
            italic_elements.append(head)

        if "bold" in body:
            bold_elements.append(head)

    return italic_elements, bold_elements


def _replaceTags(tag, italic_classes: list[str], bold_classes: list[str]) -> bool:
    for item in italic_classes:
        if item.startswith('.') and "class" in tag.attrs:
            item = item[1:]
            if tag["class"] == item:
                tag.replace_with(f"*{tag.get_text()}*")
                return True
        else:
            if tag.name == item:
                tag.replace_with(f"*{tag.get_text()}*")
                return True

    for item in bold_classes:
        if item.startswith('.') and "class" in tag.attrs:
            item = item[1:]
            if tag["class"] == item:
                tag.replace_with(f"**{tag.get_text()}**")
                return True
        else:
            if tag.name == item:
                tag.replace_with(f"**{tag.get_text()}*8")
                return True


def _processHtml(contents: str, to_replace: list[list[str]], styles: list[list[str]]) -> str:
    soup = BeautifulSoup(contents, 'xml')

    for tag in soup.find_all(True):
        replaced = _replaceTags(tag, styles[0], styles[1])
        if not replaced:
            tag.unwrap()

    contents = str(soup)

    for item in to_replace:
        contents = contents.replace(item[0], item[1])

    return contents


def epubExtractor(epub_path: str):
    files_dump = dict()
    italic_elements = list()
    bold_elements = list()

    to_replace = Settings().get("cleaner-replace")

    # Check if the file exists
    if not os.path.exists(epub_path):
        print(f"File {epub_path} does not exist.")
        return

    with zipfile.ZipFile(epub_path, 'r') as epub:
        for item in epub.namelist():
            if item.endswith(".css"):
                with epub.open(item) as f:
                    stylesheet = f.read().decode('utf-8')

                print(f"processing stylesheet {item}")
                processed_styles = _stylesheetParser(stylesheet)
                italic_elements.extend(processed_styles[0])
                bold_elements.extend(processed_styles[1])

        print("italics:", italic_elements, "\n")
        print("bolds:", bold_elements, "\n")

        # Find and open the content.opf file
        opf_file = None
        for file_name in epub.namelist():
            if file_name.endswith('content.opf'):
                opf_file = file_name
                break

        if not opf_file:
            print("content.opf file not found.")
            return

        # Get the base path for resolving chapter files
        opf_dir = os.path.dirname(opf_file)

        # Parse the content.opf file
        with epub.open(opf_file) as f:
            tree = ET.parse(f)
            root = tree.getroot()

            # Define namespaces (check your file's structure if necessary)
            namespaces = {
                'default': 'http://www.idpf.org/2007/opf'
            }

            # Find all the itemrefs that refer to chapters in the spine
            spine = root.find('default:spine', namespaces)
            manifest = {item.get('id'): item.get('href') for item in root.find('default:manifest', namespaces)}

            # Get the list of chapters in reading order
            chapters = [manifest[itemref.get('idref')] for itemref in spine.findall('default:itemref', namespaces)]

            print("Chapter files found:")
            for chapter in chapters:
                chapter_path = os.path.join(opf_dir, chapter)
                chapter_path = chapter_path.replace("\\", "/")  # Ensure correct path format
                print(chapter)
                chapter = Path(chapter)
                try:
                    with epub.open(chapter_path) as chapter_file:
                        content = chapter_file.read().decode('utf-8')
                        content = _processHtml(content, to_replace, [italic_elements, bold_elements])
                        content = content.replace("\n", "\n\n")
                        content = content.strip()
                        files_dump[chapter.stem] = content
                except KeyError as e:
                    print(f"Could not open {chapter_path}: {e}")
            print(f"total of {len(files_dump.keys())}")

    return files_dump
