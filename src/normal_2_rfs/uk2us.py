
def _makeReplaces(words: list[str]) -> list[str]:
    for index in range(0, len(words)):

        words[index] = words[index].replace('‘', '“')

        if '’' in words[index]:
            word = words[index]
            length = len(word)

            for offset in range(0, length):
                position = length - 1 - offset

                if word[position] in ['*', ',']:
                    continue
                if word[position] == '’':
                    words[index] = word[:position] + '”' + word[position+1:]
                break

    return words


def UK2US(contents: str) -> str:
    paragraphs = contents.split("\n\n")
    processed_paras = list()

    for para in paragraphs:
        lines = para.split("\n")
        processed_lines = list()

        for line in lines:
            words = line.split(' ')

            processed_words = _makeReplaces(words)

            processed_lines.append(' '.join(processed_words))

        processed_paras.append("\n".join(processed_lines))

    return "\n\n".join(processed_paras)