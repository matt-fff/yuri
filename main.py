from typing import Optional

import typer
import asyncio
from loguru import logger

from yuri.config import Config, ConfigFactory
from yuri.listener import ListenerFactory
from yuri.speaker import SpeakerFactory
from yuri.lights import Lights
from yuri.input import Input
from yuri.servos import Servos
# from yuri.textgen import TextGen

app = typer.Typer()

DEFAULT_CONFIG_LOCATION = "yuri.json"


def get_config(config_path: Optional[str]) -> Config:
    config_path = config_path or DEFAULT_CONFIG_LOCATION
    return ConfigFactory.create(config_path)

@app.command()
def respond(prompt: str, config_path: Optional[str] = None):
    config = get_config(config_path)
    # tg = TextGen(config)
    # tg.generate(prompt)
    logger.error("respond is not yet implemented")


@app.command()
def servos(config_path: Optional[str] = None):
    config = get_config(config_path)
    servos = Servos(config)
    servos.rotate()



@app.command()
def converse(max_seconds: Optional[int] = None, config_path: Optional[str] = None):
    config = get_config(config_path)
    logger.error("converse is not yet implemented")

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


async def asay(message: str, config: Config):
    servos = Servos(config)
    speaker = SpeakerFactory.create(config)
    await asyncio.gather(servos.eyes.loop(), speaker.say(message))

@app.command()
def say(message: str, config_path: Optional[str] = None):
    config = get_config(config_path)
    asyncio.run(asay(message, config))
    

@app.command()
def transcribe(config_path: Optional[str] = None):
    config = get_config(config_path)
    listener = ListenerFactory.create(config)
    audio = listener.listen()
    transcription = listener.transcribe(audio)
    logger.info(transcription)

@app.command()
def calibrate(config_path: Optional[str] = None):
    config = get_config(config_path)
    servos = Servos(config)
    speaker = SpeakerFactory.create(config)
    asyncio.run(speaker.say("Let's calibrate."))
    inputs = Input(config)
    servos.eyes.calibrate(inputs, config)
    config.save(config_path or DEFAULT_CONFIG_LOCATION)

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
