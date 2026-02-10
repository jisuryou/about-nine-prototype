import numpy as np
from dtaidistance import dtw


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

    response_a, response_b = [], []

    for i in range(1, len(conv)):
        prev = conv[i - 1]
        cur = conv[i]
        rt = max(0, (cur["start"] - prev["end"]) * 1000)

        if cur["speaker"] == conv[0]["speaker"]:
            response_a.append(rt)
        else:
            response_b.append(rt)

    if len(response_a) < 2 or len(response_b) < 2:
        return {"score": 0}

    dist = dtw.distance(response_a, response_b)
    score = int((1 / (1 + dist / 100)) * 100)

    return {"score": score}


class RhythmAnalyzer:
    def score(self, conversation_obj):
        data = _normalize_conversation(conversation_obj)
        raw = analyze(data)
        return {
            "scores": {
                "rhythm_synchrony": float(raw.get("score", 0)),
            },
            "raw": raw,
        }
