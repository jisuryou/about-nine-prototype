PREF_WORDS = ["like", "love", "favorite", "enjoy"]


def analyze(conversation_data):
    text = " ".join(u["text"].lower() for u in conversation_data["conversation"])
    count = sum(text.count(w) for w in PREF_WORDS)

    return {"score": min(100, count * 10)}
