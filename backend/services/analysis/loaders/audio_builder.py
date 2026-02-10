import subprocess
import glob
import os


def find_m3u8(directory: str):
    files = glob.glob(os.path.join(directory, "*.m3u8"))
    if not files:
        raise RuntimeError("m3u8 not found")
    return files[0]


def m3u8_to_wav(m3u8_path: str, wav_path: str):
    subprocess.run([
        "ffmpeg",
        "-y",
        "-i", m3u8_path,
        "-ac", "1",
        "-ar", "16000",
        wav_path
    ], check=True)


def build_wav_from_directory(directory: str):
    m3u8 = find_m3u8(directory)
    wav = os.path.join(directory, "audio.wav")
    m3u8_to_wav(m3u8, wav)
    return wav
