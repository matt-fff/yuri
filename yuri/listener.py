from abc import abstractmethod, ABCMeta
from dataclasses import dataclass
from typing import Callable

from loguru import logger
import speech_recognition as sr

from yuri.config import Config


@dataclass
class Transcription:
    text: str


class Listener(metaclass=ABCMeta):
    def __init__(self, config: Config):
        self.config = config

    @abstractmethod
    def listen(self):
        raise NotImplementedError()

    @abstractmethod
    def transcribe(self, audio) -> Transcription:
        raise NotImplementedError()


# TODO speech_recognition isn't maintained. The transcription is too slow.
# Find something faster.
class SpeechRecognitionListener(Listener):
    def __init__(self, config: Config):
        super().__init__(config)
        self.mic = sr.Microphone()
        self.recognizer = sr.Recognizer()
        
    @property
    def recognize(self) -> Callable[[sr.AudioData], str]:
        listener_type = self.config.listener_type
        transcribe_name = f"recognize_{listener_type}"
        if not hasattr(self.recognizer, transcribe_name):
            raise ValueError(f"{listener_type} is not a valid listener type")

        return getattr(self.recognizer, transcribe_name)


    def listen(self) -> sr.AudioData:
        logger.info("listen.start")

        with self.mic as source:
            logger.debug("adjusting")
            self.recognizer.adjust_for_ambient_noise(source)

            logger.debug("listening")
            audio = self.recognizer.listen(source)

        logger.info("listen.done")
        return audio

    def transcribe(self, audio: sr.AudioData) -> Transcription:
        logger.info("transcribe.start")

        transcription = self.recognize(audio)

        logger.info("transcribe.done")
        return Transcription(text=transcription)


class ListenerFactory:
    @classmethod
    def create(cls, config: Config) -> Listener:
        return SpeechRecognitionListener(config)
