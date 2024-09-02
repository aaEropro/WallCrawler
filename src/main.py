import shutil
import os
import sys
from pathlib import Path
import logging
import logging.config
import logging.handlers
import yaml

from src.name_detection import nameDetection
from src.content_refactoring import contentRefactoring
from src.context_aware_punctuation import contextAwarePunctuation
from src.false_positives_correction import falsePositivesCorrection
from src.settings import Settings
from src.epub_files_rectifier import epubFilesRectifier
from src.epub_extractor import epubExtractor


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


def _processes(content: str) -> str | None:
    if type(content) is not str:
        log.error(f"expected string, got {type(content)}")
        return None

    names: list[str] = nameDetection(content)
    content: str = contentRefactoring(content, names)
    content: str = falsePositivesCorrection(content)
    content: str = contextAwarePunctuation(content)

    return content


def run() -> None:
    with open(Path("logger.yml")) as file:  # set up logging
        logger_config = yaml.safe_load(file)
    logging.config.dictConfig(logger_config)

    Settings()  # instantiate settings singleton

    input_dir = Path(Settings().get("input-dir"))
    output_dir = Path(Settings().get("output-dir"))

    # if not input_dir.exists():
    #     log.info("aborted during input dir check")
    #     sys.exit(1)
    if not _verifyDirExists(output_dir):
        log.info("aborted during output dir check")
        sys.exit(1)

    # files_dump = epubFilesRectifier(input_dir)
    files_dump = epubExtractor(input_dir)
    if files_dump is None:
        sys.exit(1)

    for file_name in files_dump.keys():
        output_file_path = Path(output_dir, file_name + ".md")

        content = _processes(files_dump[file_name])
        if content is None:
            sys.exit(1)
        else:
            with open(output_file_path, mode="wt", encoding="utf8") as f:
                f.write(content)
