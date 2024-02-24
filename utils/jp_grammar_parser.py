import dango

part_dict = {
    "NOUN": "名詞",
    "NAME": "人名",
    "PLACE_NAME": "地名",
    "NUMBER": "数詞",
    "COUNTER": "助数詞",
    "PRONOUN": "代名詞",
    "VERB": "動詞",
    "ADJECTIVE": "形容詞",
    "ADJECTIVAL_NOUN": "形状詞",
    "ADVERB": "副詞",
    "PARTICLE": "助詞",
    "AUXILIARY_VERB": "助動詞",
    "PRE_NOUN_ADJECTIVAL": "連体詞",
    "INTERJECTION": "感動詞",
    "SUFFIX": "接尾辞",
    "CONJUNCTION": "接続詞",
    "PREFIX": "接頭辞"
}


def parse(content):
    parsed = []
    for chunk in dango.tokenize(content):
        word = chunk.surface
        part = str(chunk.part_of_speech)
        root = chunk.dictionary_form if chunk.dictionary_form else word
        if part in part_dict.keys():
            part_detail = part_dict[part]
        else:
            part_detail = "その他"
        parsed.append({"word": word, "root": root, "part": part, "part_detail": part_detail})
    return parsed
