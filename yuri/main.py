import os
from io import BytesIO

import typer
from loguru import logger
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

from yuri.listener import ListenerFactory
from yuri.speaker import SpeakerFactory

app = typer.Typer()


@app.command()
def say(message: str, speaker_type: str = "google"):
    speaker = SpeakerFactory.create(speaker_type=speaker_type)
    speaker.say(message)


@app.command()
def transcribe(listener_type: str = "sphinx"):
    listener = ListenerFactory.create(listener_type=listener_type)
    audio = listener.listen()
    transcription = listener.transcribe(audio)
    logger.info(transcription)


@app.command()
def repeat(listener_type: str = "sphinx", speaker_type: str = "google"):
    listener = ListenerFactory.create(listener_type=listener_type)
    audio = listener.listen()
    transcription = listener.transcribe(audio)

    logger.info(transcription)

    speaker = SpeakerFactory.create(speaker_type=speaker_type)
    speaker.say(transcription.text)


if __name__ == "__main__":
    app()
