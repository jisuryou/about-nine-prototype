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
    texts = [u["text"] for u in conversation_data["conversation"]]
    avg_len = sum(len(t.split()) for t in texts) / max(len(texts), 1)

    score = min(100, int(avg_len * 2))
    return {"score": score}


class DiscourseAnalyzer:
    def score(self, conversation_obj):
        data = _normalize_conversation(conversation_obj)
        raw = analyze(data)
        return {
            "scores": {
                "topic_continuity": float(raw.get("score", 0)),
            },
            "raw": raw,
        }
