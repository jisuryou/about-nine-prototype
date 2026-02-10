def analyze(conversation_data):
    texts = [u["text"] for u in conversation_data["conversation"]]
    avg_len = sum(len(t.split()) for t in texts) / max(len(texts), 1)

    score = min(100, int(avg_len * 2))
    return {"score": score}
