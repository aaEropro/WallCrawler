from src.mailman.settings import Settings
from src.processor.cleaner import clean_word


def _decide_correct(line: str, false_positives: list) -> str:
    words_list = line.split()

    if len(words_list) < 2:
        return " ".join(words_list)

    first_word = clean_word(words_list[0])
    second_word = clean_word(words_list[1])

    # check if the work is not in the list
    if first_word.lower() not in false_positives:
        return " ".join(words_list)

    # check if the word is followed by a lowercase word
    if (not first_word.islower()) and second_word.islower():
        words_list[0] = words_list[0].lower()

    return " ".join(words_list)


def _smart_split(content: str, sep: list[str]) -> list[str]:
    strings = list()
    last_index = 0

    for current_index, char in enumerate(content[:-1]):
        if char in sep:
            portion = content[last_index:current_index]
            if portion:
                strings.append(portion)
            last_index = current_index+1

    portion = content[last_index:]
    if portion:
        strings.append(portion)

    return strings


def ignore_false_positives(content: str) -> str:
    lines_list = content.split("\n\n")
    processed_lines = list()

    # get the false positives list
    false_positives = Settings().get("false-positives", "ignore")
    if not false_positives:
        print("WARNING: no false positives list.")
        return content

    for line in lines_list:
        sentences = line.split(". ")
        processed_sentences = list()

        # print(sentences)

        for sentence in sentences:
            sentence = _decide_correct(sentence, false_positives)
            processed_sentences.append(sentence)

        # print(processed_sentences)

        processed_lines.append(". ".join(processed_sentences))

    return "\n\n".join(processed_lines)


if __name__ == "__main__":
    text = """she made steady. Teresa must have thought. A cow."""

    print(ignore_false_positives(text))
