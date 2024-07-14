from processor.cleaner import strip_word, clean_word


def _extend_name(name: str) -> str:
    """
    creates the possessive of a name.
    :param name: name.
    :return: name+"s" or "name"
    """
    if name[-1] != 's':
        return name+'s'
    else:
        return name


def _word_is_name(word: str, names: list) -> str:
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


def lowercase_non_names(text: str, names: list) -> str:
    text = text.strip()
    lines = text.split('\n\n')
    normalized_lines = list()
    processed_line = list()

    for line in lines:
        line = line.strip()
        words = line.split()
        processed_line.clear()

        for word in words:
            processed_line.append(_word_is_name(word, names))

        normalized_lines.append(' '.join(processed_line))

    return '\n\n'.join(normalized_lines)


def _insert_tags(word: str) -> str:
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


def _is_name(word: str, prev_word: str) -> bool:
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


def detect_names(text: str) -> [str, list]:
    """
    detect the names inside a text.
    :param text: the text containing names.
    :return: the text with names marked with tags and the list of names detected.
    """
    names_set = set()
    processed_lines = list()

    lines = text.split('\n\n')

    for line in lines:
        line = line.strip()
        line_words = line.split(" ")

        for index, word in enumerate(line_words):

            if index != 0 and _is_name(word, line_words[index-1]):
                # mark the found word with HTML tags
                line_words[index] = _insert_tags(word)
                # add the name to the list
                word = strip_word(word)
                names_set.add(word)
                names_set.add(_extend_name(word))

        processed_lines.append(' '.join(line_words).replace('</ft> <ft>', ' '))

    return '\n\n'.join(processed_lines), sorted(list(names_set))
