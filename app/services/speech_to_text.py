import os
import tempfile
import whisper


model = whisper.load_model("base")


def transcribe_audio(file_bytes: bytes, suffix: str = ".mp3") -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
        temp_audio.write(file_bytes)
        temp_audio_path = temp_audio.name

    try:
        result = model.transcribe(temp_audio_path)
        raw_text = result.get("text", "")
                              
        if isinstance(raw_text, list):
            raw_text = " ".join([str(x) for x in raw_text])
        
        
        text =str(raw_text).strip()

        if not text:
            raise ValueError("No speech detected in the audio.")

        return text
    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)