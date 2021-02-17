import os
from io import BytesIO

import typer
from loguru import logger
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

from yuri.listener import SRListener
from yuri.speaker import SpeakerFactory

app = typer.Typer()


@app.command()
def say(message: str):
    speaker = SpeakerFactory.create()
    speaker.say(message)


@app.command()
def transcribe(listener_type: str = "sphinx"):
    listener = SRListener(listener_type)
    for transcription in listener.transcribe():
        logger.info(transcription)


@app.command()
def repeat():
    listener = ListenerFactory.create()
    transcription = listener.transcribe()

    speaker = SpeakerFactory.create()
    speaker.say(transcription)


if __name__ == "__main__":
    app()
