from utils.settings import Settings


def _inList(word: str) -> bool:
    target_words = Settings().get("context-aware", "target-terms")

    for item in target_words:
        if item in word:
            return True

    return False


def _isName(word: str, names: list[str]) -> bool:
    for item in ['*', '"', '“', '”', "'", ".", ',', '…', ':', "?", "!"]:
        word = word.replace(item, '')

    return word in names


def _nextIsNot(source: str, current_position: int, searched: str):
    if current_position == len(source) - 1:
        return False
    if source[current_position + 1] != searched:
        return True
    
    return False


def _checkContext(words: list[str], names: list[str]) -> list[str]:
    awareness_threshold = int(Settings().get("context-aware", "awareness-threshold"))
    list_length = len(words)
    processed_words = list()

    for word_index in range(list_length):
        is_sentance_end = True
        word = words[word_index]
        word_length = len(word)
        problem_char_index = None
        for char_index, char in enumerate(word):
            if char in ['?', '!']:
                problem_char_index = char_index
            elif char == '…':
                if char_index + 1 < word_length and word[char_index + 1] != '.':
                    problem_char_index = char_index
                if word_index == list_length - 1 and char_index == word_length - 1:
                    problem_char_index = char_index
        if problem_char_index is None:
            processed_words.append(word)
            continue
    
        if word_index == list_length - 1:
            is_sentance_end = True
        else:
            next_word = words[word_index + 1]

            if next_word.islower():
                is_sentance_end = False
            else:
                offset_threshold = min(awareness_threshold, list_length - word_index - 1)  # maximum safe distance to check ahead
                for offset in range(1, offset_threshold + 1):
                    if _inList(words[word_index + offset]) or '.' in words[word_index + offset]:
                        is_sentance_end = False
            
        if is_sentance_end:
            processed_words.append(word[:problem_char_index+1] + '.' + word[problem_char_index+1:])
        else:
            processed_words.append(word[:problem_char_index+1] + ',' + word[problem_char_index+1:])

    return processed_words


def insertPunctuation(contents: str, names: list[str]) -> str:
    paragraphs = contents.split("\n\n")
    processed_paras = list()

    for para in paragraphs:
        para = para.strip()
        lines = para.split("\n")
        processed_lines = list()

        for line in lines:
            line = line.strip()
            words = line.split(' ')
            processed_lines.append(' '.join(_checkContext(words, names)))

        processed_paras.append("\n".join(processed_lines))

    return "\n\n".join(processed_paras)
