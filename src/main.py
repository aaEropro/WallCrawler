import shutil
import os
import sys
from pathlib import Path

from src.processor.name import detect_names, lowercase_non_names
from src.processor.cleaner import sanitize_text
from src.processor.epub import process_html
from src.processor.context_aware import analyze_context
from src.processor.false_positives import ignore_false_positives
from src.mailman.settings import Settings


def _verify_dir_exists(path: Path) -> bool:
    if not path.exists():
        print(f"dir {str(path)} does not exist")
        try:
            os.mkdir(path)
            print(f"created dir {str(path)}")
        except Exception as error:
            print(f"error when trying to create dir: {error}")
            return False

    return True


def _run_processes(content: str) -> str:
    """
    runs each file through the process.
    :param content: plain text content for processing.
    :return: processed content.
    """
    content = sanitize_text(content)
    tagged_content, names = detect_names(content)
    content = lowercase_non_names(content, names)
    content = ignore_false_positives(content)
    content = analyze_context(content)

    return content


def _txt_mode(input_dir: Path, output_dir: Path):

    files_list = [item for item in input_dir.iterdir() if item.is_file()]

    for file in files_list:

        if file.suffix != ".txt":
            shutil.copyfile(file, Path(output_dir, file.name))
            continue

        with open(file, mode="r", encoding="utf-8") as f:
            content = f.read()

        content = _run_processes(content)

        with open(Path(output_dir, file.stem+".md"), mode="w", encoding="utf-8") as f:
            f.write(content)


def _epub_mode(input_dir: Path, output_dir: Path) -> None:

    export_intermediate = Settings().get("export-intermediate")
    intermediate_dir = Path(Settings().get("intermediate-dir"))
    if export_intermediate and not _verify_dir_exists(intermediate_dir):
        print("aborted during intermediate dir check")
        sys.exit(1)

    files = [item for item in input_dir.iterdir() if item.is_file() and item.suffix == ".html"]
    for file in files:
        with open(file, mode="r", encoding="utf-8") as f:
            content = f.read()

        content = process_html(content)
        content = content.replace("\n", "\n\n")

        if export_intermediate:
            with open(Path(intermediate_dir, str(file.stem)+".md"), mode="w", encoding="utf-8") as f:
                f.write(content)

        content = _run_processes(content)

        with open(Path(output_dir, str(file.stem)+".md"), mode="w", encoding="utf-8") as f:
            f.write(content)


def run():
    settings_instance = Settings()

    # get the input and output folders
    input_dir = Path(Settings().get("input-dir"))
    output_dir = Path(Settings().get("output-dir"))

    if not _verify_dir_exists(input_dir):
        print("aborted during input dir check")
        sys.exit(1)
    if not _verify_dir_exists(output_dir):
        print("aborted during output dir check")

    # mode bypasses
    if Settings().get("mode") == "epub":
        _epub_mode(input_dir, output_dir)
    if Settings().get("mode") == "txt":
        _txt_mode(input_dir, output_dir)
