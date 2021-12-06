from abc import abstractmethod, ABCMeta
from dataclasses import dataclass

from loguru import logger
import speech_recognition as sr


@dataclass
class Transcription:
    text: str


class Listener(metaclass=ABCMeta):
    @abstractmethod
    def listen(self):
        raise NotImplementedError()

    @abstractmethod
    def transcribe(self, audio) -> Transcription:
        raise NotImplementedError()


class SpeechRecognitionListener(Listener):
    def __init__(self, listener_type: str):
        self.mic = sr.Microphone()
        self.recognizer = sr.Recognizer()

        transcribe_name = f"recognize_{listener_type}"
        if not hasattr(self.recognizer, transcribe_name):
            raise ValueError(f"{listener_type} is not a valid listener type")

        self.recognize = getattr(self.recognizer, transcribe_name)

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
        return transcription


class ListenerFactory:
    @classmethod
    def create(cls, listener_type: str = "sphinx") -> Listener:
        return SpeechRecognitionListener(listener_type)
