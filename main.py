#!/usr/bin/env python

from typing import Optional

import typer
import asyncio
import pyaudio
import wave
from rich.console import Console
from loguru import logger

from yuri.config import Config, ConfigFactory
from yuri.listener import ListenerFactory
from yuri.speaker import SpeakerFactory
from yuri.lights import Lights
from yuri.input import Input
from yuri.servos import ServosFactory
from yuri.yuri import Yuri

# from yuri.textgen import TextGen

app = typer.Typer()
console = Console()

DEFAULT_CONFIG_LOCATION = "yuri.json"



def user_input() -> str:
    return console.input(prompt="[bold blue]>>>[/bold blue] ")


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
def converse(
    max_seconds: Optional[int] = None, config_path: Optional[str] = None
):
    config = get_config(config_path)
    logger.error("converse is not yet implemented")

@app.command()
def set_audio_in(config_path: Optional[str] = None):
    config = get_config(config_path)

    audio = pyaudio.PyAudio()
    info = audio.get_host_api_info_by_index(0)

    def print_device_options():
        for i in range(int(info.get('deviceCount', 0))):
            if int(audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels', 0)) > 0:
                console.print("Input device id ", i, " - ", audio.get_device_info_by_host_api_device_index(0, i).get('name'))

        console.print("Select the desired input device ID") 

    print_device_options()
    
    device_id = None
    while True:
        try:
            device_id = int(user_input())
            break
        except Exception as exc:
            console.print(repr(exc))
            console.print("Yikes. Wanna try again?\n")
            print_device_options()
    
    console.print(f"Saving input device {device_id} to configuration...")
    config.listener.device_index = device_id
    config.save(config_path or DEFAULT_CONFIG_LOCATION)

@app.command()
def set_audio_out(config_path: Optional[str] = None):
    config = get_config(config_path)

    audio = pyaudio.PyAudio()
    info = audio.get_host_api_info_by_index(0)

    def print_device_options():
        for i in range(int(info.get('deviceCount', 0))):
            if int(audio.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels', 0)) > 0:
                console.print("Output device id ", i, " - ", audio.get_device_info_by_host_api_device_index(0, i).get('name'))

        console.print("Select the desired output device ID") 

    print_device_options()
    
    device_id = None
    while True:
        try:
            device_id = int(user_input())
            break
        except Exception as exc:
            console.print(repr(exc))
            console.print("Yikes. Wanna try again?\n")
            print_device_options()
    
    console.print(f"Saving output device {device_id} to configuration...")
    config.speaker.device_index = device_id
    config.save(config_path or DEFAULT_CONFIG_LOCATION)


@app.command()
def inputs(seconds: int = 10, config_path: Optional[str] = None):
    config = get_config(config_path)
    inputs = Input(config)
    inputs.demo(seconds)


@app.command()
def colors(seconds: int = 3, config_path: Optional[str] = None):
    config = get_config(config_path)
    lights = Lights(config)
    asyncio.run(lights.cycle_colors(seconds))


@app.command()
def say(message: str, config_path: Optional[str] = None):
    config = get_config(config_path)
    speaker = SpeakerFactory.create(config)
    asyncio.run(speaker.say(message))


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
    servos = ServosFactory.create(config)
    speaker = SpeakerFactory.create(config)
    inputs = Input(config)

    asyncio.run(servos.calibrate(inputs, speaker=speaker))
    config.save(config_path or DEFAULT_CONFIG_LOCATION)


@app.command()
def repeat(config_path: Optional[str] = None):
    config = get_config(config_path)

    listener = ListenerFactory.create(config)
    audio = listener.listen()
    transcription = listener.transcribe(audio)

    logger.info(transcription)

    speaker = SpeakerFactory.create(config)
    asyncio.run(speaker.say(transcription.text))

@app.command()
def run(config_path: Optional[str] = None):
    config = get_config(config_path)
    yuri = Yuri(config)
    asyncio.run(yuri.run())


if __name__ == "__main__":
    app()
