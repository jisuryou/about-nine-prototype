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
