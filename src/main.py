from pathlib import Path
import sys


from utils.cli import cli
from utils import log
from utils.settings import Settings
import pipeline


if __name__ == "__main__":
    Settings()
    
    run_parameters = cli(sys.argv) # parse the run arguments
    if run_parameters["epub"] is None:
        log.error("no EPUB path provided")
        sys.exit(1);

    if run_parameters["output"] is None:
        run_parameters["output"] = Path(run_parameters["epub"].parent, run_parameters["epub"].stem)
    if type(run_parameters["intermediate"]) is bool and run_parameters["intermediate"] is True:
        run_parameters["intermediate"] = Path(str(run_parameters["output"]) + " - original")

    log.info(f"parsed parameters: {run_parameters}")

    pipeline.pipeline(run_parameters)
