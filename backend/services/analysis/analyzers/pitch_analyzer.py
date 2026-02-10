import librosa
import numpy as np


def analyze(wav_path):
    y, sr = librosa.load(wav_path)

    f0, _, _ = librosa.pyin(y, fmin=65, fmax=400)

    f0 = f0[np.isfinite(f0)]

    if len(f0) == 0:
        return {"score": 0}

    var = np.var(f0)
    score = int(min(100, var / 10))

    return {"score": score}


class PitchAnalyzer:
    def score(self, wav_paths_by_speaker=None, wav_paths=None, call_id=None):
        paths = []
        if isinstance(wav_paths_by_speaker, dict) and wav_paths_by_speaker:
            paths = list(wav_paths_by_speaker.values())
        elif isinstance(wav_paths, list):
            paths = wav_paths

        scores = []
        for path in paths:
            if not path:
                continue
            try:
                out = analyze(path)
                scores.append(float(out.get("score", 0)))
            except Exception:
                continue

        avg_score = float(sum(scores) / len(scores)) if scores else 0.0
        return {
            "scores": {"voice_pitch": avg_score},
            "raw": {"per_file": scores, "call_id": call_id},
        }
