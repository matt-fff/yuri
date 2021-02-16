import os
from io import BytesIO

import typer
from loguru import logger
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play


def say(message: str):
    typer.echo(message)
    mp3_fp = BytesIO()
    tts = gTTS(message, lang="en")
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    play(AudioSegment.from_mp3(mp3_fp))


def main(name: str):
    say(f"Hello {name}")


if __name__ == "__main__":
    typer.run(main)
