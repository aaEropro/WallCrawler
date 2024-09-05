from settings import Settings


def _inList(word: str) -> bool:
    target_words = Settings().get("context-aware", "target-terms")

    for item in target_words:
        if item in word:
            return True

    return False


def _checkContext(words: list[str]) -> list[str]:
    awareness_threshold = int(Settings().get("context-aware", "awareness-threshold"))
    list_length = len(words)
    processed_words = list()

    for index in range(list_length):
        word = words[index]
        if ('?' not in word) and ('!' not in word):  # ignore words not containing `?` or `!
            processed_words.append(word)
            continue

        offset_threshold = min(awareness_threshold, list_length - index - 1)  # maximum safe distance to check ahead
        for offset in range(1, offset_threshold + 1):
            if _inList(words[index + offset]) or '.' in words[index + offset]:
                word = word.replace('?', "?,")
                word = word.replace('!', "!,")
                break
        else:
            word = word.replace("?", "?.")
            word = word.replace("!", "!.")

        processed_words.append(word)

    return processed_words


def contextAwarePunctuation(contents: str) -> str:
    paragraphs = contents.split("\n\n")
    processed_paras = list()

    for para in paragraphs:
        para = para.strip()
        lines = para.split("\n")
        processed_lines = list()

        for line in lines:
            line = line.strip()
            words = line.split(' ')
            processed_lines.append(' '.join(_checkContext(words)))

        processed_paras.append("\n".join(processed_lines))

    return "\n\n".join(processed_paras)
