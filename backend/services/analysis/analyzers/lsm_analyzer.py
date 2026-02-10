def analyze(conversation_data):
    conv = conversation_data["conversation"]

    speakers = {}
    for u in conv:
        speakers.setdefault(u["speaker"], []).append(u["text"])

    if len(speakers) < 2:
        return {"score": 0}

    a, b = list(speakers.values())

    words_a = set(" ".join(a).split())
    words_b = set(" ".join(b).split())

    score = int(len(words_a & words_b) / max(len(words_a | words_b), 1) * 100)
    return {"score": score}
