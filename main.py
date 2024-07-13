import shutil
import os
import sys

from dataclass.name import detect_names, lowercase_non_names
from dataclass.cleaner import sanitize_text
from mailman.settings import Settings


def run(input_path: str, output_path: str, filename: str):
    """
    runs each file through the process.
    :param input_path: input directory.
    :param output_path: output directory.
    :param filename: current file name.
    :return: None.
    """

    with open(os.path.join(input_path, filename), 'r', encoding='utf8') as file:
        content = file.read()

    content = sanitize_text(content)
    tagged_content, names = detect_names(content)
    content = lowercase_non_names(content, names)

    with open(os.path.join(output_path, filename), 'w', encoding='utf8') as file:
        file.write(content)


if __name__ == '__main__':
    settings_instance = Settings()

    # get the input and output folders
    input_folder = Settings().get("last-opened", 'input-dir')
    output_folder = Settings().get("last-opened", 'output-dir')
    # convert forward slashes to backward slashes
    input_folder = str(os.path.normpath(input_folder))
    output_folder = str(os.path.normpath(output_folder))
    if input_folder is None or output_folder is None:
        print("either input or output folder is missing.")
        sys.exit()

    if not os.path.isdir(input_folder):
        print('input directory error.')
        sys.exit()
    if not os.path.isdir(output_folder):
        os.mkdir(output_folder)

    for path, directories, files in os.walk(input_folder):
        for item in files:
            if item.endswith('.txt'):
                run(path, output_folder, item)
            else:
                shutil.copyfile(os.path.join(path, item), os.path.join(output_folder, item))
