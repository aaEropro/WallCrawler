from epub_extractor.css_element import CSSElement
from utils import log


def _parse(stylesheet: str, contains: str) -> list:
    """
    Extracts CSS selectors that contain a specified string from a stylesheet.

    Parameters:
    - stylesheet: A string containing the CSS stylesheet to parse.
    - contains: A string to search for in the CSS rules.

    Returns:
    - A list of `CSSElement` objects for selectors that match the specified property or value.
    """
        
    stylesheet = stylesheet.strip()
    elements = stylesheet.split('}')
    resault = list()

    for element in elements[:-1]:
        element = element.strip()
        parts = element.split('{')
        if len(parts) < 2:
            log.error(f"error, not closed: '{element}'")
            continue

        head = parts[0].strip()
        body = parts[1].strip().lower()

        if '@' in head:
            continue

        if contains in body:
            resault.append(CSSElement(head))

    return resault


def getCSSSelectors(stylesheet: str, contains: list[str]):
    """
    Extracts CSS selectors for multiple properties or values from a stylesheet.

    Parameters:
    - stylesheet: A string containing the CSS stylesheet to parse.
    - contains: A list of strings to search for in the CSS rules.

    Returns:
    - A list of lists, each containing `CSSElement` objects for selectors matching the specified criteria.
    """
    resaults = list()

    for item in contains:
        resaults.append(_parse(stylesheet, item))

    return resaults