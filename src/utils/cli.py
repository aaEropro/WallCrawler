from pathlib import Path


from utils import log


def cli(args) -> dict:
    print(f"[ INFO  ]: run parameters: {args}")

    parameters = {
        "epub": None,
        "intermediate": None,
        "output": None
    }

    arguments = list()

    for item in args[1:]:  # consolidate arguments
        if item.startswith('-'):
            arguments.append([item.lower()])
        elif len(arguments) > 0:
            arguments[-1].append(item)
        else:
            log.error(f"orphan argument {item}")

    for item in arguments:  # process arguments
        if len(item) < 2:
            if item[0] == "-i" or item[0] == "-intermediate":
                parameters["intermediate"] = True
        else:
            if item[0] == "-e" or item[0] == "-epub":
                parameters["epub"] = Path(item[1])
            if item[0] == "-i" or item[0] == "-intermediate":
                parameters["intermediate"] = Path(item[1])
            if item[0] == "-o" or item[0] == "-output":
                parameters["output"] = Path(item[1])

    return parameters
