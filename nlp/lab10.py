import string

import nltk as nltk
import stanza
import spacy_stanza
import matplotlib.pyplot as plt
import transformers
import langdetect

def read_text_into_string(path: str) -> str:
    with open(path, 'rb') as file:
        content = file.read()
        decoded_content = content.decode('utf-8')
        _tokens = [_token.rstrip(string.punctuation).lstrip(string.punctuation) for _token in decoded_content.split() if any(char.isalpha() for char in _token)] # remove punctuation
        return ' '.join(_tokens)


if __name__ == '__main__':
    nltk.download('punkt_tab')

    stanza.download('ro')
    nlp = spacy_stanza.load_pipeline('ro')

    text_str = read_text_into_string("text.txt")
    detected_lang = langdetect.detect(text_str)
    if detected_lang != 'ro':
        print(f"Textul este în limba {detected_lang}")
        exit(1)
    doc = nlp(text_str)

    for token in doc:
        print(token.text, token.lemma_, token.pos_, token.dep_)

    tokens = nltk.word_tokenize(text_str)
    token_lengths = [len(token) for token in tokens]
    length_distribution = nltk.FreqDist(token_lengths)
    freq_distr = nltk.FreqDist(tokens)
    freq_distr.plot(10)
    plt.show()
    length_distribution.plot(15)
    plt.show()

