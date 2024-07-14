from mailman.settings import Settings


def _is_hit(word: str) -> bool:
    """
    verifies if the given word is in a list of target words.
    :param word:
    :return:
    """
    target_words = Settings().get("context-aware", "target-terms")
    for item in target_words:
        if item in word:
            return True

    return False


def _check_context(words_list: list) -> list[str]:
    """
    for each word in the list, it looks forward a number of words and checks if there should
    be a comma or a period after `?` and `!`.
    :param words_list:
    :return:
    """
    awareness_threshold = int(Settings().get("context-aware", "awareness-threshold"))
    list_length = len(words_list)
    processed_words = list()

    for index, word in enumerate(words_list):
        # ignore words not containing `?` or `!`.
        if ("?" not in word) and ("!" not in word):
            processed_words.append(word)
            continue

        # the maximum safe distance to look forward without getting out of the list.
        offset_threshold = min(awareness_threshold, list_length-index-1)
        for offset in range(1, offset_threshold+1):
            # if it hits a target word force comma.
            if _is_hit(words_list[index+offset]):
                word = word.replace("?", "?,")
                word = word.replace("!", "!,")
                break
            # if it hits a period before a target word, force period.
            if "." in words_list[index+offset]:
                word = word.replace("?", "?.")
                word = word.replace("!", "!.")
                break
        # if no hit, force period.
        else:
            word = word.replace("?", "?.")
            word = word.replace("!", "!.")

        processed_words.append(word)

    return processed_words


def analyze_context(contents: str) -> str:
    """
    goes through the given text and places a comma or a period after every
    question mark or exclamation mark, depending on the context.

    assumes markdown-style text, lines separated by double newline.
    :param contents:
    :return:
    """
    lines = contents.split("\n\n")
    processed_lines = list()

    for line in lines:
        words = line.split(" ")
        processed_words = _check_context(words)
        processed_lines.append(" ".join(processed_words))

    return "\n\n".join(processed_lines)


if __name__ == "__main__":
    text = '"Holden?" her husband said, incredulously. "James Holden put Cortazar up to killing Teresa?"'

    print(analyze_context(text))
