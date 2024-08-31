
def _matchWords(words: list[str], names: list[str]) -> list[str]:
    processed_words = list()

    for word in words:
        word_copy = word
        for item in ['*', '"', '“', '”', "'", ".", ',', '…', ':', "?", "!"]:
            word_copy = word_copy.replace(item, '')

        if word_copy == "I" or word_copy.startswith("I’"):  # ignore variations of "I"
            processed_words.append(word)
        elif word.islower():  # ignore lowercase words
            processed_words.append(word)
        elif word_copy in names:  # ignore names
            processed_words.append(word)
        elif word_copy.isupper():  # ignore all upper words (usually acronyms)
            processed_words.append(word)
        else:
            processed_words.append(word.lower())

    return processed_words


def contentRefactoring(text: str, names: list[str]) -> str:
    paragraphs = text.split("\n\n")
    processed_paras = list()

    for para in paragraphs:
        para = para.strip()
        lines = para.split("\n")
        processed_lines = list()

        for line in lines:
            line = line.strip()
            words = line.split(' ')

            processed_words = _matchWords(words, names)
            processed_lines.append(' '.join(processed_words))

        processed_paras.append("\n".join(processed_lines))

    return "\n\n".join(processed_paras)
