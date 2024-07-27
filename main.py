import shutil
import os
import sys

from processor.name import detect_names, lowercase_non_names
from processor.cleaner import sanitize_text
from processor.epub import process_html
from processor.context_aware import analyze_context
from processor.false_positives import ignore_false_positives
from mailman.settings import Settings


def run(content: str) -> str:
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


def txt_mode(input_dir: str, output_dir: str):
    for current_dir, _, files_list in os.walk(input_dir):
        for file_name in files_list:
            input_file_path = os.path.join(current_dir, file_name)
            output_file_path = os.path.join(output_dir, file_name)

            if file_name.endswith('.txt'):
                with open(input_file_path, mode="r", encoding="utf-8") as file:
                    content = file.read()
                content = run(content)
                with open(output_file_path, mode="w", encoding="utf-8") as file:
                    file.write(content)
            else:
                shutil.copyfile(input_file_path, output_file_path)


def epub_mode(input_dir: str, output_dir: str):
    export_intermediate = Settings().get("settings", "export-intermediate")
    intermediate_dir = Settings().get("last-opened", "intermediate-dir")
    if export_intermediate and not os.path.isdir(intermediate_dir):
        os.mkdir(intermediate_dir)

    for current_dir, _, files_list in os.walk(input_dir):
        for file_name in files_list:

            if not file_name.endswith("html"):
                continue

            input_file_path = os.path.join(current_dir, file_name)
            with open(input_file_path, mode="r", encoding="utf-8") as file:
                content = file.read()

            content = process_html(content)
            content = content.replace("\n", "\n\n")

            if export_intermediate:
                intermediate_file_path = os.path.join(intermediate_dir, file_name[:-4]+"md")
                with open(intermediate_file_path, mode="w", encoding="utf-8") as file:
                    file.write(content)

            content = run(content)

            output_file_path = os.path.join(output_dir, file_name[:-4]+"md")
            with open(output_file_path, mode="w", encoding="utf-8") as file:
                file.write(content)


if __name__ == '__main__':
    settings_instance = Settings()

    # get the input and output folders
    input_dir = Settings().get("last-opened", "input-dir")
    output_dir = Settings().get("last-opened", "output-dir")
    # convert forward slashes to backward slashes
    input_dir = str(os.path.normpath(input_dir))
    output_dir = str(os.path.normpath(output_dir))
    if input_dir is None or output_dir is None:
        print("either input or output folder is missing.")
        sys.exit()

    # verify specified directories exist
    if not os.path.isdir(input_dir):
        print("input directory error.")
        sys.exit()
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    # mode bypasses
    if Settings().get("settings", "mode") == "epub":
        epub_mode(input_dir, output_dir)
    if Settings().get("settings", "mode") == "txt":
        txt_mode(input_dir, output_dir)


