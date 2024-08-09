from src.processor.cleaner import strip_word, clean_word


def _wordIsName(word: str, names: list) -> str:
    word = word.strip()
    word_copy = word.replace('<ft>', '').replace('</ft>', '')
    word_copy = strip_word(word_copy)

    if word_copy == "I" or word_copy.startswith("I’"):
        return word
    if word.isupper():
        return word
    if word_copy not in names:
        return word.lower()

    return word


def lowercaseNonNames(text: str, names: list) -> str:
    text = text.strip()
    lines = text.split('\n\n')
    normalized_lines = list()
    processed_line = list()

    for line in lines:
        line = line.strip()
        words = line.split()
        processed_line.clear()

        for word in words:
            processed_line.append(_wordIsName(word, names))

        normalized_lines.append(' '.join(processed_line))

    return "\n\n".join(normalized_lines)


def _insertTag(word: str) -> str:
    """
    inserts the "<ft>" "</ft>" tags at the root of the word.
    :param word: word.
    :return: word + tags.
    """
    length = len(word)
    index = 0

    while word[length - 1 - index] in ['*', '"', '”', "'", ',', '?', '!', ':', ';', '…', '.']:
        index += 1
    word = f'{word[:length-index]}</ft>{word[length-index:]}'

    index = 0
    while word[index] in ['*', '"', '”', "'", ',', '?', '!', ':', ';', '…', '.']:
        index += 1
    word = f'{word[:index]}<ft>{word[index:]}'

    return word


def _extendName(name: str) -> str:
    """
    creates the possessive of a name.
    :param name: name.
    :return: name+"s" or "name"
    """
    if name[-1] != 's':
        return name+'s'
    else:
        return name


def _isName(word: str, prev_word: str) -> bool:
    """
    decide if the word is a name inside a sentence.
    :param word: possible name.
    :param prev_word: previous word in sentence.
    :return:
    """
    # skip variation of "I" pronoun
    if word == "I" or word.startswith("I’"):
        return False
    # skip lowercase words
    if word.islower():
        return False
    # skip start of speech
    if word[0] in ['"', '“']:
        return False

    word = strip_word(word)
    prev_word = clean_word(prev_word)

    # skip 0-length words
    if len(word) == 0:
        return False
    # skip lowercase words
    if word.islower():
        return False
    # skip start of sentence
    if len(prev_word) > 0 and prev_word[-1] in [".", '?', '!', '…', ':']:
        return False

    return True


def detectNames(text: str, mark: bool = False) -> [str, list]:
    """
    detect the names inside a text.
    :param text: the text containing names.
    :param mark: indicates if it should mark the first appearance of a name.
    :return: the text with names marked with tags and the list of names detected.
    """
    names_set = set()
    processed_lines = list()

    lines_list = text.split('\n\n')

    for line in lines_list:
        line = line.strip()
        words_list = line.split()

        for index, word in enumerate(words_list):
            if index > 0 and _isName(word, words_list[index - 1]):
                if mark:
                    words_list[index] = _insertTag(word)
                word = strip_word(word)
                names_set.add(word)
                names_set.add(_extendName(word))

        processed_lines.append(' '.join(words_list).replace("</ft> <ft>", ' '))

    return "\n\n".join(processed_lines), sorted(list(names_set))
