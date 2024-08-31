from pathlib import Path
import logging
import os
from bs4 import BeautifulSoup

from src.settings import Settings


log = logging.getLogger(__name__)


def _verifyDirExists(path: Path) -> bool:
    if not path.exists():
        log.info(f"dir {str(path)} does not exist")
        try:
            os.mkdir(path)
            log.info(f"created dir {str(path)}")
        except Exception as error:
            log.error(f"error when trying to create dir: {error}")
            return False

    return True


def _replaceTags(tag, italic_classes: list, bold_classes: list, bolditalic_classes: list) -> bool:
    # print(tag.name)
    for item in italic_classes:
        if item == tag.name or ("class" in tag.attrs and item == tag["class"]):
            tag.replace_with(f"*{tag.get_text()}*")
            return True

    for item in bold_classes:
        if item == tag.name or ("class" in tag.attrs and item == tag["class"]):
            tag.replace_with(f"**{tag.get_text()}**")
            return True

    for item in bolditalic_classes:
        if item == tag.name or ("class" in tag.attrs and item == tag["class"]):
            tag.replace_with(f"***{tag.get_text()}***")
            return True


def _processHtml(contents: str, to_replace: list[list[str]]) -> str:
    italic_classes: list[str] = Settings().get("current-stylesheet", "italic")
    static_italic_classes: list[str] = Settings().get("current-stylesheet", "static-italic")
    bold_classes: list[str] = Settings().get("current-stylesheet", "bold")
    static_bold_classes: list[str] = Settings().get("current-stylesheet", "static-bold")
    bolditalic_classes: list[str] = Settings().get("current-stylesheet", "bold-italic")
    static_bolditalic_classes: list[str] = Settings().get("current-stylesheet", "static-bold-italic")

    italic_classes.extend(static_italic_classes)
    bold_classes.extend(static_bold_classes)
    bolditalic_classes.extend(static_bolditalic_classes)

    soup = BeautifulSoup(contents, 'xml')

    for tag in soup.find_all(True):
        replaced = _replaceTags(tag, italic_classes, bold_classes, bolditalic_classes)
        if not replaced:
            tag.unwrap()

    contents = str(soup)

    for item in to_replace:
        contents = contents.replace(item[0], item[1])

    return contents


def epubFilesRectifier(input_dir: Path) -> dict[str] | None:
    export_intermediate = Settings().get("export-intermediate")
    intermediate_dir = Path(Settings().get("intermediate-dir"))
    if export_intermediate and not _verifyDirExists(intermediate_dir):
        log.info("aborted during intermediate dir check")
        return None

    files = [item for item in input_dir.iterdir() if item.is_file() and item.suffix in [".html", ".xhtml"]]

    files_dump = dict()

    to_replace = Settings().get("cleaner-replace")

    for file in files:
        with open(file, mode="r", encoding="utf-8") as f:
            content = f.read()

        content = _processHtml(content, to_replace)
        content = content.replace("\n", "\n\n")

        if export_intermediate:
            with open(Path(intermediate_dir, str(file.stem)+".md"), mode="w", encoding="utf-8") as f:
                f.write(content)

        files_dump[file.stem] = content

    return files_dump
