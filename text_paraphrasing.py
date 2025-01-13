import spacy
from transformers import AutoTokenizer, AutoModelForMaskedLM, pipeline
import random
import nltk
from nltk.corpus import wordnet as wn

# incarca spacy pt romana
try:
    nltk.download('wordnet')
    nltk.download('omw-1.4')
    nlp = spacy.load('ro_core_news_sm')
except:
    import spacy.cli

    spacy.cli.download('ro_core_news_sm')
    nlp = spacy.load('ro_core_news_sm')

model_name = "dumitrescustefan/bert-base-romanian-cased-v1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForMaskedLM.from_pretrained(model_name)


def get_hypernyms(word):
    hypernyms = set()
    for synset in wn.synsets(word, lang='ron'):
        for hyper in synset.hypernyms():
            for lemma in hyper.lemmas('ron'):
                hypernyms.add(lemma.name().replace('_', ' '))
    return list(hypernyms)


def get_negated_antonym(word):
    for synset in wn.synsets(word, lang='ron'):
        for lemma in synset.lemmas('ron'):
            if lemma.antonyms():
                antonym = lemma.antonyms()[0].name().replace('_', ' ')
                return antonym
    return None


def get_bert_synonym(token, new_text, i):
    masked_sentence = " ".join(new_text[:i] + ["[MASK]"] + new_text[i + 1:])
    pipe = pipeline('fill-mask', model=model, tokenizer=tokenizer)
    predictions = pipe(masked_sentence)
    for pred in predictions:
        if pred['token_str'] != token.text and len(pred['token_str']) > 2:  # ignora cuvintele scurte
            return pred['token_str']
    return None


def get_replacement(token, new_text, i):
    methods = random.choices(
        ['bert', 'hypernym', 'antonym'],
        weights=[0.65, 0.175, 0.175],  # distributie de probabilitate
        k=3  # in caz ca nu merge prima metoda, incercam si celelalte
    )

    for method in methods:
        if method == 'bert':
            synonym = get_bert_synonym(token, new_text, i)
            if synonym:
                return synonym

        elif method == 'hypernym':
            hypernyms = get_hypernyms(token.text)
            if hypernyms:
                return random.choice(hypernyms)

        elif method == 'antonym':
            antonym = get_negated_antonym(token.text)
            if antonym:
                return f"nu {antonym}"

    # pastram cuvantul original daca nu am gasit o inlocuire
    return token.text


def paraphrase_text(text, change_threshold=0.5):
    doc = nlp(text)
    tokens = [token.text for token in doc]
    new_text = tokens.copy()

    changed_count = 0
    for i, token in enumerate(doc):
        if token.is_alpha:
            if random.random() < change_threshold:
                replacement = get_replacement(token, new_text, i)
                if replacement != token.text:
                    changed_count += 1
                new_text[i] = replacement
            else:
                new_text[i] = token.text

    result = " ".join(new_text)
    percent_changed = (changed_count / len(tokens)) * 100
    return result, percent_changed


if __name__ == "__main__":
    texts = [
        "Câinele se joacă până la epuizare în zilele calde de vară, iar iarna doarme mult lângă soba caldă din sufragerie.",
        "Copiii aleargă zăpăciți prin parcul mare din centru și se joacă frumos jocurile lor preferate.",
        "Profesorul răbdator explică încet și coerent lecția nouă despre inteligență artificială.",
        "În pădurea deasă, animalele înfometate caută hrană curată și apă potabilă.",
        "Grădina din spatele casei este plină de flori colorate și parfumate. Este și un copac fructifer înalt și bătrân.",
        "Păsările călătoare zboară sus pe cer în formații impresionante. Deobicei, se opresc la lacul rece din apropiere pentru a se odihni puțin.",
        "Bătrânul bunic povestește amintiri din tinerețe la focul cald de tabără. Poveștile sale sunt pline de aventuri palpitante și învățăminte.",
        "Cartea nouă de literatură are ilustrații frumoase. Este o poveste interesantă despre un tânăr curajos și o prințesă fermecătoare.",
        "Elevii cuminți rezolvă probleme dificile la matematică, cu ajutorul profesorului de matematică bine pregătit.",
        "Automobilul puternic și roșu accelerează rapid pe autostradă lungă și largă.",
        "Doctorul tânăr examinează atent pacientul bolnav și recomandă un tratament potrivit.",
        "Orașul vechi are clădiri istorice superbe și o mulțime străzi înguste.",
        "Turistul curios admiră peisajele montane și face poze des.",
        "Actorii pricepuți repetă încontinuu replicile pentru piesa de teatru, care începe curând.",
        "Librăria veche conține cărți rare și ediții limitate. Este un loc liniștit și plăcut pentru pasionații de lectură.",
    ]

    for idx, original_text in enumerate(texts):
        paraphrased_text, change_percent = paraphrase_text(original_text)
        print(f"Exemplu {idx + 1}:")
        print(f"Text original: {original_text}")
        print(f"Text parafrazat: {paraphrased_text}")
        print(f"Procent de cuvinte modificate: {change_percent:.2f}%")
        print("-" * 80)

