import zipfile
from pathlib import Path
from xml.etree import ElementTree
import urllib.parse
from pathlib import PurePosixPath


from epub_extractor.css_element import CSSElement
from epub_extractor.chapter_processing import processChapter
from epub_extractor.stylesheet_parser import getCSSSelectors
from utils import log


def epubExtractor(epub_path: Path) -> dict[str, str] | None:
    """
    converts an EPUB to Markdown.
    """
    files_dump = dict()
    content = str()
    epub = zipfile.ZipFile(epub_path, mode='r')


    ## search for specific CSS selectors in all stylesheets
    selectors = [
        [CSSElement('i'), CSSElement("em")], 
        [CSSElement('b'), CSSElement("strong")]
    ]
    for file_name in epub.namelist():
        if file_name.endswith(".css"):
            with epub.open(file_name) as f:
                stylesheet = f.read().decode('utf-8')
            resault = getCSSSelectors(stylesheet, ["italic", "bold"])
            selectors[0].extend(resault[0])
            selectors[1].extend(resault[1])
    log.info(selectors[0])
    log.info(selectors[1])


    ## get all split paths
    opf_file = None
    for file_name in epub.namelist():
        if file_name.lower().endswith(".opf"):
            opf_file = file_name
            break
    if opf_file is None:
        log.error("'.opf' file not found inside the EPUB")
        return None
    
    with epub.open(opf_file) as f:
        tree = ElementTree.parse(f)
    namespaces = {'default': 'http://www.idpf.org/2007/opf'}
    root = tree.getroot()
    spine = root.find("default:spine", namespaces)
    manifest = {item.get("id"): item.get("href") for item in root.find("default:manifest", namespaces)}
    split_names = [manifest[itemref.get("idref")] for itemref in spine.findall("default:itemref", namespaces)]

    opf_dir = PurePosixPath(opf_file).parent
    split_paths = [PurePosixPath(opf_dir, urllib.parse.unquote(item)) for item in split_names]


    ## convert splits from HTML to MD
    for split_path in split_paths:
        try:
            with epub.open(str(split_path)) as split_file:
                content: str = split_file.read().decode('utf-8')
        except KeyError as e:
            log.error(f"Could not open {split_path}: {e}")

        if content:
            content = processChapter(content, selectors)
            files_dump[split_path.stem] = content.strip()

    log.info(f"Read a total of {len(files_dump.keys())} splits")

    return files_dump