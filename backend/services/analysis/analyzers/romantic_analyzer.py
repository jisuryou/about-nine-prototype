KEYWORDS = ["love", "miss", "like you", "together"]


def _normalize_conversation(conversation_obj):
    if isinstance(conversation_obj, dict) and "conversation" in conversation_obj:
        return conversation_obj
    conv = getattr(conversation_obj, "conversation", None)
    if conv is None:
        return {"conversation": []}
    normalized = []
    for u in conv:
        if isinstance(u, dict):
            normalized.append(u)
        else:
            normalized.append(
                {
                    "speaker": getattr(u, "speaker", None),
                    "start": getattr(u, "start", None),
                    "end": getattr(u, "end", None),
                    "text": getattr(u, "text", ""),
                }
            )
    return {"conversation": normalized}


def analyze(conversation_data):
    text = " ".join(u["text"].lower() for u in conversation_data["conversation"])
    count = sum(text.count(k) for k in KEYWORDS)

    return {"score": min(100, count * 20)}


class RomanticAnalyzer:
    def score(self, conversation_obj):
        data = _normalize_conversation(conversation_obj)
        raw = analyze(data)
        return {
            "scores": {
                "romantic_intent": float(raw.get("score", 0)),
            },
            "raw": raw,
        }
