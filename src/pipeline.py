import os
import shutil
import sys
from pathlib import Path

from utils import log
from normal_2_rfs.name_detection import nameDetection
from normal_2_rfs.content_refactoring import contentRefactoring
from normal_2_rfs.punctuation_insertion import insertPunctuation
from normal_2_rfs.name_fp_correction import falsePositivesCorrection
from utils.settings import Settings
from epub_extractor.epub_extractor import epubExtractor
from normal_2_rfs.uk2us import UK2US


def _validate_parameters(parameters: dict) -> bool:
    if parameters["epub"] is None:
        log.error("no EPUB path provided")
        return False
    if not parameters["epub"].is_file():
        log.error(f"EPUB path provided does not point to a file: {parameters['epub']}")
        return False
    if not parameters["epub"].suffix == ".epub":
        log.error(f"the provided input file is not an EPUB")
        return False

    if parameters["intermediate"] is not None:
        if parameters["intermediate"].exists():
            log.info("using existing intermediate directory")
        else:
            os.mkdir(parameters["intermediate"])
            log.info(f"created intermediate directory {parameters['intermediate']}")

    if parameters["output"] is None:
        log.error("no output path provided")
        return False
    if parameters["output"].exists():
        log.warning("output directory exists; contents have been deleted")
        shutil.rmtree(parameters["output"])
        os.mkdir(parameters["output"])
    else:
        os.mkdir(parameters["output"])
        log.info(f"created directory {parameters['output']}")
    
    return True


def pipeline(parameters: dict) -> None:
    is_valid = _validate_parameters(parameters)
    if not is_valid:
        return

    files_dump = epubExtractor(parameters["epub"])
    if files_dump is None:
        log.error("EpubExtractor did not return anything")
        sys.exit(1)

    for file_name in files_dump.keys():
        content: str = files_dump[file_name]

        if parameters["intermediate"]:
            with open(Path(parameters["intermediate"], file_name + ".md"), mode="wt", encoding="utf8") as f:
                f.write(content)

        if Settings().get("modules", "uk2us"):
            content: str = UK2US(content)

        names: list[str] = nameDetection(content)
        content: str = insertPunctuation(content, names)
        content: str = contentRefactoring(content, names)
        content: str = falsePositivesCorrection(content)

        with open(Path(parameters["output"], file_name + ".md"), mode="wt", encoding="utf8") as f:
            f.write(content)