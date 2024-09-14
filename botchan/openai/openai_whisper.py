from typing import Any

import structlog

from botchan.openai import CLIENT as client

logger = structlog.getLogger(__name__)


class OpenAiWhisper:
    def transcribe(self, audio_file_path: str) -> str:
        # FIXME(zf): seems to have issue on long audio messages.
        audio_file = open(audio_file_path, "rb")
        transcription = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file
        )
        logger.info("whisper", audio_file=audio_file_path, transcription=transcription)
        return transcription.text