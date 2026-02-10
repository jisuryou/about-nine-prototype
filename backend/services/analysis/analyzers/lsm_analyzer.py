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


class LSMAnalyzer:
    def score(self, conversation_obj):
        data = _normalize_conversation(conversation_obj)
        raw = analyze(data)
        return {
            "scores": {
                "lsm": float(raw.get("score", 0)),
            },
            "raw": raw,
        }
