from abc import abstractmethod, ABCMeta
from io import BytesIO
from typing import Optional

import pyttsx3

from gtts import gTTS
from loguru import logger
from pydub import AudioSegment
from pydub.playback import play

from yuri.config import Config


class Speaker(metaclass=ABCMeta):
    def __init__(self, config: Optional[Config]):
        self.config = config

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

        play(AudioSegment.from_mp3(mp3_fp))
        logger.info("say.done", message=message)


class Ttsx3Speaker(Speaker):
    def __init__(self, config: Config):
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
        "pyttsx3": Ttsx3Speaker,
        "fake": FakeSpeaker,
    }

    @classmethod
    def create(cls, config: Config) -> Speaker:
        speaker_type = config.speaker.speaker_type
        if speaker_type not in cls.SPEAKERS:
            raise ValueError(f"{speaker_type} is invalid")

        return cls.SPEAKERS[speaker_type](config)
