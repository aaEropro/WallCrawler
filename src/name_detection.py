
def _traverseWords(words: list[str]) -> set[str]:
    names = set()
    length = len(words)

    if length < 2:
        return names

    for index in range(1, length):
        curr_word = words[index]
        prev_word = words[index - 1]

        if curr_word.islower():  # skip lowercase words
            continue
        if curr_word[0] in ['"', '“']:  # skip start of speech
            continue

        for item in ['*', '"', '“', '”', "'", "’", "‘", ".", ',', '…', ':', "?", "!"]:
            curr_word = curr_word.replace(item, "")
        for item in ['*', ',', '"', '“', '”', "'", "‘", "’"]:
            prev_word = prev_word.replace(item, "")

        if len(curr_word) == 0:  # skip 0-length words
            continue
        if len(prev_word) > 0 and prev_word[-1] in [".", '?', '!', '…', ':']:  # skip start of sentence
            continue

        names.add(curr_word)
        if curr_word != 'I' and not curr_word.endswith('s'):
            names.add(curr_word + 's')

    return names


def nameDetection(text: str) -> list[str]:
    names = set()
    paragraphs = text.split("\n\n")

    for para in paragraphs:
        para = para.strip()
        lines = para.split("\n")

        for line in lines:
            line = line.strip()
            words = line.split()

            names.update(_traverseWords(words))

    return list(names)
