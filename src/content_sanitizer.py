from settings import Settings


def contentSanitizer(text: str) -> str:
    to_replace = Settings().get("cleaner-replace")

    for item in to_replace:
        text = text.replace(item[0], item[1])

    return text
