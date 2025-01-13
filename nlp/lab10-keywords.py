from transformers import T5Tokenizer, T5ForConditionalGeneration
import yake

from lab10 import read_text_into_string

if __name__ == "__main__":
    language='en'
    max_ngram_size=2
    deduplication_threshold=0.9
    num_keywords=5

    text_str = read_text_into_string("text.txt")
    custom_kw_extractor = yake.KeywordExtractor(
        lan=language,
        n=max_ngram_size,
        dedupLim=deduplication_threshold,
        top=num_keywords,
        features=None
    )

    keywords = custom_kw_extractor.extract_keywords(text_str)



    for kw in keywords:
        print(kw[0])

    tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-large")
    model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-large")

    for kw in keywords:
        key_words = kw[0].split()
        for key_word in key_words:
            key_word = '"' + key_word + '"'
        key_words = ', '.join(key_words)
        prompt = f'Generate a long phrase with: {key_words}.'
        input_ids = tokenizer(prompt, return_tensors="pt").input_ids
        outputs = model.generate(input_ids,max_length=200)
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f'Keywords: {kw[0]}\n\tGenerated text: {result}')
