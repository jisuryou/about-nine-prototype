import whisper

model = whisper.load_model("base")


def wav_to_segments(wav_path: str, speaker: str):
    result = model.transcribe(wav_path, word_timestamps=True)

    segments = []
    for seg in result["segments"]:
        segments.append({
            "speaker": speaker,
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"]
        })

    return segments
