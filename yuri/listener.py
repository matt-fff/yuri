from abc import abstractmethod, ABCMeta
from typing import List

from loguru import logger
import speech_recognition


class Listener(metaclass=ABCMeta):
    @abstractmethod
    def transcribe(self) -> List[str]:
        raise NotImplementedError()


class SRListener(Listener):
    def __init__(self, type_key: str):
        self.mic = speech_recognition.Microphone()
        self.recognizer = speech_recognition.Recognizer()
        self.type_key = type_key

    def transcribe(self) -> List[str]:
        logger.info("transcribe.start")

        with self.mic as source:
            logger.debug("adjusting")
            self.recognizer.adjust_for_ambient_noise(source)

            logger.debug("listening")
            audio = self.recognizer.listen(source)

            transcriptions = []
            logger.debug("recognizing")
            for type_key in self.type_key.split(","):
                transcription = getattr(self.recognizer, f"recognize_{type_key}")(audio)
                transcriptions.append(transcription)
                logger.debug(f"{type_key}: {transcription}")

        logger.info("transcribe.done")
        return transcriptions
