from src.settings import Settings


def _decideCorrect(words: list[str], false_positives: list[str]) -> list[str]:
    list_length = len(words)

    if list_length < 3:
        return words

    for index in range(1, list_length - 1):
        prev_word = words[index - 1]
        curr_word = words[index]
        next_word = words[index + 1]

        if '.' not in prev_word:  # if not sentence start ignore selection
            continue

        if curr_word.islower():  # if sentence start is lowercase ignore selection
            continue

        for item in ['*', ',', '"', '“', '”', "'", '’']:  # clean selection
            prev_word = prev_word.replace(item, '')
            curr_word = curr_word.replace(item, '')
            next_word = next_word.replace(item, '')

        if curr_word.lower() not in false_positives:  # if sentence start not in false positives list ignore selection
            continue

        if (not curr_word.islower()) and next_word.islower():  # force sentence start to lowercase
            words[index] = words[index].lower()

    return words


def falsePositivesCorrection(content: str) -> str:
    false_positives = Settings().get("false-positives", "ignore")
    if not false_positives:
        print("WARNING: no false positives list.")
        return content

    paragraphs = content.split("\n\n")
    processed_paras = list()

    for para in paragraphs:
        para = para.strip()
        lines = para.split('\n')
        processed_lines = list()

        for line in lines:
            line = line.strip()
            words = line.split(' ')
            processed_lines.append(' '.join(_decideCorrect(words, false_positives)))

        processed_paras.append("\n".join(processed_lines))

    return "\n\n".join(processed_paras)
