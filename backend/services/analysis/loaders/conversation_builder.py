# backend/services/analysis/conversation_builder.py

from typing import List, Dict
import os
import whisper
import threading

# -------------------------
# Whisper lazy loader
# -------------------------
_model = None
_model_lock = threading.Lock()

def get_whisper_model():
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                _model = whisper.load_model("base")
    return _model


# -------------------------
# Single audio → segments
# -------------------------
def audio_to_segments(
    wav_path: str,
    speaker_id: str,
) -> List[Dict]:
    """
    단일 화자 오디오 파일 → conversation segment 리스트
    """
    if not os.path.exists(wav_path) or os.path.getsize(wav_path) < 1024:
        return []

    model = get_whisper_model()

    try:
        result = model.transcribe(
            wav_path,
            word_timestamps=False,   # segment 단위면 충분
            language="en",            # 필요 시 자동 감지 제거
            fp16=False                # CPU 안정성
        )
    except Exception:
        return []

    segments = []
    for seg in result.get("segments", []):
        text = seg["text"].strip()
        if not text:
            continue

        segments.append({
            "speaker": speaker_id,
            "start": float(seg["start"]),
            "end": float(seg["end"]),
            "text": text
        })

    return segments


# -------------------------
# Multiple speakers merge
# -------------------------
def build_conversation(
    call_id: str,
    speaker_audio_map: Dict[str, str],
) -> Dict:
    """
    여러 화자의 wav 파일을 받아
    time 기준으로 정렬된 conversation 생성

    speaker_audio_map = {
        "uid_1": "/tmp/a.wav",
        "uid_2": "/tmp/b.wav"
    }
    """

    all_segments: List[Dict] = []

    for speaker_id, wav_path in speaker_audio_map.items():
        segments = audio_to_segments(wav_path, speaker_id)
        all_segments.extend(segments)

    # 시간 기준 정렬
    all_segments.sort(key=lambda x: x["start"])

    return {
        "call_id": call_id,
        "conversation": all_segments
    }


class ConversationBuilder:
    def build(
        self,
        call_id: str,
        wav_items: List[Dict],
        uid_mapping: Dict | None = None,
        participants: List[str] | None = None,
    ) -> Dict:
        speaker_audio_map: Dict[str, str] = {}
        speaker_wavs: Dict[str, str] = {}

        for idx, item in enumerate(wav_items or []):
            if not isinstance(item, dict):
                continue
            wav_path = item.get("wav_path")
            if not wav_path:
                continue

            speaker_id = item.get("speaker_hint")
            uid = item.get("uid")

            if not speaker_id and uid_mapping and uid is not None:
                speaker_id = uid_mapping.get(str(uid)) or uid_mapping.get(uid)

            if not speaker_id and uid is not None:
                speaker_id = f"uid_{uid}"

            if not speaker_id and participants and idx < len(participants):
                speaker_id = str(participants[idx])

            if not speaker_id:
                speaker_id = f"speaker_{idx + 1}"

            speaker_audio_map[speaker_id] = wav_path
            speaker_wavs[speaker_id] = wav_path

        conv = build_conversation(call_id=call_id, speaker_audio_map=speaker_audio_map)
        conv["speaker_wavs"] = speaker_wavs
        return conv
