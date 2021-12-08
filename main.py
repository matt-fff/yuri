import os
from io import BytesIO
from typing import Optional

import typer
from loguru import logger
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

from yuri.config import Config, ConfigFactory
from yuri.listener import ListenerFactory
from yuri.speaker import SpeakerFactory

app = typer.Typer()

DEFAULT_CONFIG_LOCATION = "yuri-config.yaml"


def get_config(config_path: Optional[str]) -> Config:
    config_path = config_path or DEFAULT_CONFIG_LOCATION
    return ConfigFactory.create(config_path)


@app.command()
def say(message: str, config_path: Optional[str] = None):
    config = get_config(config_path)
    speaker = SpeakerFactory.create(config)
    speaker.say(message)


@app.command()
def transcribe(config_path: Optional[str] = None):
    config = get_config(config_path)
    listener = ListenerFactory.create(config)
    audio = listener.listen()
    transcription = listener.transcribe(audio)
    logger.info(transcription)


@app.command()
def repeat(config_path: Optional[str] = None):
    config = get_config(config_path)

    listener = ListenerFactory.create(config)
    audio = listener.listen()
    transcription = listener.transcribe(audio)

    logger.info(transcription)

    speaker = SpeakerFactory.create(config)
    speaker.say(transcription.text)


if __name__ == "__main__":
    app()
