import importlib.util
from typing import Any


class VoiceService:
    def status(self) -> dict[str, Any]:
        faster_whisper = importlib.util.find_spec("faster_whisper") is not None
        piper = importlib.util.find_spec("piper") is not None
        return {
            "ok": True,
            "stt_ready": faster_whisper,
            "tts_ready": piper,
            "orb_ready": True,
            "plain_english": "Voice/orb shell integration is scaffolded. Local voice engines can be wired in when installed.",
            "next_action": "Install local STT/TTS engines later to upgrade the shell from visual voice status to real voice interaction.",
        }


voice_service = VoiceService()
