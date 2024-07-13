


def _insert_tags(word:str) -> str:
    lenght = len(word)
    index = 0
    while (word[lenght-1-index] in ['*', '"', '”', "'", ',', '?', '!', ':', ';', '…', '.']):
        index += 1
    word = f'{word[:lenght-index]}</ft>{word[lenght-index:]}'

    index = 0
    while (word[index] in ['*', '"', '”', "'", ',', '?', '!', ':', ';', '…', '.']):
        index += 1
    word = f'{word[:index]}<ft>{word[index:]}'

    return word



print(_insert_tags('"text"'))