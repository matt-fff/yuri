from abc import abstractmethod, ABCMeta
from io import BytesIO
from typing import Optional

import pyttsx3
import pyaudio

from gtts import gTTS
from loguru import logger
from pydub import AudioSegment
from pydub.utils import make_chunks

from yuri.config import SpeakerConfig, Config


class Speaker(metaclass=ABCMeta):
    SAMPLE_RATES = sorted([32000, 44100, 48000, 96000, 128000], reverse=True)

    def __init__(self, config: SpeakerConfig):
        self.config = config

    def open_stream(self, segment: AudioSegment) -> pyaudio.Stream:
        pa = pyaudio.PyAudio()
        
        format_ = pyaudio.paInt16
        if segment.sample_width:
            format_ = pa.get_format_from_width(segment.sample_width)

        for rate in [segment.frame_rate] + self.SAMPLE_RATES:
            for channels in range(segment.channels or 2, 0, -1):
                try:
                    if not rate or pa.is_format_supported(rate,
                             output_channels=channels,
                             output_format=format_
                    ):
                        continue

                    # TODO let's get a context manager going
                    return pa.open(format=format_,
                        channels=channels,
                        rate=rate,
                        input=False,
                        output=True,
                    )
                except ValueError:
                    pass

        raise ValueError("No valid sample rate detected for output device")

    def play(self, segment: AudioSegment):
        pa = pyaudio.PyAudio()
        stream = self.open_stream(segment)

        # Just in case there were any exceptions/interrupts, we release the resource
        # So as not to raise OSError: Device Unavailable should play() be used again
        try:
            # break audio into half-second chunks (to allows keyboard interrupts)
            for chunk in make_chunks(segment, 500):
                stream.write(chunk._data)
        finally:
            stream.stop_stream()
            stream.close()

            pa.terminate()


    @abstractmethod
    async def say(self, message: str):
        raise NotImplementedError()


class FakeSpeaker(Speaker):
    def __init__(self, *args):
        super().__init__(None if not args else args[0])

    async def say(self, message: str):
        logger.info(message)


class GoogleSpeaker(Speaker):
    async def say(self, message: str):
        logger.info("say.start", message=message)

        mp3_fp = BytesIO()
        tts = gTTS(message, lang="en", tld="ru")
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)

        self.play(AudioSegment.from_mp3(mp3_fp))

        logger.info("say.done", message=message)


class Ttsx3Speaker(Speaker):
    def __init__(self, config: SpeakerConfig):
        self.config = config
        self.engine = pyttsx3.init()
        # voices 2, 13, 14, 17
        # 61 = Russian
        # 62 = Slovak
        self.engine.setProperty(
            "voice", self.engine.getProperty("voices")[15].id
        )
        self.engine.setProperty("rate", 160)

    async def say(self, message: str):
        logger.info("say.start", message=message)
        self.engine.say(message)
        self.engine.runAndWait()
        logger.info("say.done", message=message)


class SpeakerFactory:
    SPEAKERS = {
        "google": GoogleSpeaker,
        "ttsx3": Ttsx3Speaker,
        "fake": FakeSpeaker,
    }

    @classmethod
    def create(cls, config: Config) -> Speaker:
        speaker_type = config.speaker.engine
        if speaker_type not in cls.SPEAKERS:
            raise ValueError(f"{speaker_type} is invalid")

        return cls.SPEAKERS[speaker_type](config.speaker)
