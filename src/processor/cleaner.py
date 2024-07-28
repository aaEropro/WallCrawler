from src.mailman.settings import Settings


def _allow_overrides(contents: str) -> str:
    titles = Settings().get("titles")
    special_strings = Settings().get("cleaner-special-strings")

    for item in titles:
        contents = contents.replace(item+".", item.lower())
    for item in special_strings:
        contents = contents.replace(item, item.lower())

    return contents


def sanitize_text(text: str) -> str:
    to_replace = Settings().get("cleaner-replace")

    for item in to_replace:
        text = text.replace(item[0], item[1])
    text = _allow_overrides(text)

    return text


def strip_word(word: str) -> str:
    markers = ['*', '"', '“', '”', "'", ".", ',', '…', ':', "?", "!"]

    for item in markers:
        word = word.replace(item, '')

    return word


def clean_word(word: str) -> str:
    markers = ['*', ',', '"', '“', '”', "'", "’"]

    for item in markers:
        word = word.replace(item, '')

    return word
