import shutil
import os
import sys
from pathlib import Path
import logging
import logging.config
import logging.handlers
import yaml

from name_detection import nameDetection
from content_refactoring import contentRefactoring
from context_aware_punctuation import contextAwarePunctuation
from false_positives_correction import falsePositivesCorrection
from settings import Settings
from epub_extractor import epubExtractor


log = logging.getLogger(__name__)


def run(parameters: dict) -> None:
    if parameters["epub"] is None:
        log.error("no EPUB path provided")
        sys.exit(1)
    if not parameters["epub"].is_file():
        log.error(f"EPUB path provided does not point to a file: {parameters['epub']}")
        sys.exit(1)
    if not parameters["epub"].suffix == ".epub":
        log.error(f"the provided input file is not an EPUB")
        sys.exit(1)

    if parameters["intermediate"] is not None and parameters["intermediate"].exists():
        log.warning("intermediate directory exists; contents have been deleted")
        shutil.rmtree(parameters["intermediate"])
        os.mkdir(parameters["intermediate"])
    else:
        os.mkdir(parameters["intermediate"])
        log.info(f"created directory {parameters['intermediate']}")

    if parameters["output"] is None:
        log.error("no output path provided")
        sys.exit(1)
    if parameters["output"].exists():
        log.warning("output directory exists; contents have been deleted")
        shutil.rmtree(parameters["output"])
        os.mkdir(parameters["output"])
    else:
        os.mkdir(parameters["output"])
        log.info(f"created directory {parameters['output']}")


    files_dump = epubExtractor(parameters["epub"])
    if files_dump is None:
        log.error("EpubExtractor did not return anything")
        sys.exit(1)

    for file_name in files_dump.keys():
        content = files_dump[file_name]

        if parameters["intermediate"]:
            with open(Path(parameters["intermediate"], file_name + ".md"), mode="wt", encoding="utf8") as f:
                f.write(content)

        names: list[str] = nameDetection(content)
        content: str = contentRefactoring(content, names)
        content: str = falsePositivesCorrection(content)
        content: str = contextAwarePunctuation(content)

        with open(Path(parameters["output"], file_name + ".md"), mode="wt", encoding="utf8") as f:
            f.write(content)


if __name__ == "__main__":
    run_parameters = {
        "epub": None,
        "intermediate": None,
        "output": None
    }
    arguments = list()
    Settings()  # instantiate settings singleton

    with open(Path("logger.yml")) as file:  # set up logging
        logger_config = yaml.safe_load(file)
    logging.config.dictConfig(logger_config)

    for item in sys.argv[1:]:  # consolidate arguments
        if item.startswith('-'):
            arguments.append([item.lower()])
        elif len(arguments) > 0:
            arguments[-1].append(item)
        else:
            log.error(f"orphan argument {item}")

    for item in arguments:  # process arguments
        if len(item) < 2:
            if item[0] == "-i" or item[0] == "-intermediate":
                run_parameters["intermediate"] = True

        else:
            if item[0] == "-e" or item[0] == "-epub":
                run_parameters["epub"] = Path(item[1])
            if item[0] == "-i" or item[0] == "-intermediate":
                run_parameters["intermediate"] = Path(item[1])
            if item[0] == "-o" or item[0] == "-output":
                run_parameters["output"] = Path(item[1])

    if run_parameters["output"] is None and run_parameters["epub"]:
        run_parameters["output"] = Path(run_parameters["epub"].parent, run_parameters["epub"].stem)
    if type(run_parameters["intermediate"]) is bool and run_parameters["intermediate"] is True:
        run_parameters["intermediate"] = Path(str(run_parameters["output"]) + " - original")

    log.debug(run_parameters)

    run(run_parameters)
