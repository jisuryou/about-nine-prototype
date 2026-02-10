KEYWORDS = ["love", "miss", "like you", "together"]


def analyze(conversation_data):
    text = " ".join(u["text"].lower() for u in conversation_data["conversation"])
    count = sum(text.count(k) for k in KEYWORDS)

    return {"score": min(100, count * 20)}
