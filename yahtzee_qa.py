import os
from transformers import pipeline

qa_pipeline = pipeline(
    "question-answering",
    model="distilbert/distilbert-base-cased-distilled-squad",
    tokenizer="distilbert/distilbert-base-cased-distilled-squad"
)

zeroshot_classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

CONTEXT = os.path.join(os.path.dirname(__file__), "yahtzee_context.txt")

with open(CONTEXT, "r", encoding="utf-8") as file:
    context = file.read()


def answer_question(question: str) -> str:
    candidate_labels = ["Yahtzee", "Unrelated"]
    classification_result = zeroshot_classifier(
        question,
        candidate_labels,
    )

    top_label = classification_result["labels"][0]
    top_score = classification_result["scores"][0]

    if top_label != "Yahtzee" or top_score < 0.4:
        return (
            "Sorry, I only answer questions related to Yahtzee. "
            "It seems like this question might not be about Yahtzee."
        )

    qa_result = qa_pipeline({
        'question': question,
        'context': context
    })

    answer = qa_result.get("answer", "Sorry, I don't know the answer to that question.")

    return answer


if __name__ == "__main__":
    user_question = "How do I get Yahtzee?"
    a = answer_question(user_question)
    print(f"Q: {user_question}")
    print(f"A: {a}")
