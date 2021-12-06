from abc import abstractmethod, ABCMeta
from io import BytesIO

from gtts import gTTS
from loguru import logger
from pydub import AudioSegment
from pydub.playback import play

from yuri.config import Config


class Speaker(metaclass=ABCMeta):
    def __init__(self, config: Config):
        self.config = config

    @abstractmethod
    def say(self, message: str):
        raise NotImplementedError()


class GoogleSpeaker(Speaker):
    def say(self, message: str):
        logger.info("say.start", message=message)

        mp3_fp = BytesIO()
        tts = gTTS(message, lang="en")
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)

        play(AudioSegment.from_mp3(mp3_fp))
        logger.info("say.done", message=message)


class SpeakerFactory:
    SPEAKERS = {
        "google": GoogleSpeaker,
    }

    @classmethod
    def create(cls, config: Config) -> Speaker:
        speaker_type = config.speaker_type
        if speaker_type not in cls.SPEAKERS:
            raise ValueError(f"{speaker_type} is invalid")

        return cls.SPEAKERS[speaker_type](config)
