from typing import Optional

import typer
from loguru import logger

from yuri.config import Config, ConfigFactory
from yuri.listener import ListenerFactory
from yuri.speaker import SpeakerFactory
from yuri.lights import Lights
from yuri.input import Input
# from yuri.textgen import TextGen

app = typer.Typer()

DEFAULT_CONFIG_LOCATION = "yuri.yaml"


def get_config(config_path: Optional[str]) -> Config:
    config_path = config_path or DEFAULT_CONFIG_LOCATION
    return ConfigFactory.create(config_path)

# @app.command()
# def textgen(prompt: Optional[str] = None, config_path: Optional[str] = None):
#     config = get_config(config_path)
#     tg = TextGen(config)
#     tg.generate(prompt)

@app.command()
def inputs(seconds: int = 10, config_path: Optional[str] = None):
    config = get_config(config_path)
    inputs = Input(config)
    inputs.demo(seconds)

@app.command()
def colors(seconds: int = 3, config_path: Optional[str] = None):
    config = get_config(config_path)
    lights = Lights(config)
    lights.cycle_colors(seconds)


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
