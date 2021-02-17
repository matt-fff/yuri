from abc import abstractmethod, ABCMeta
from io import BytesIO

from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play


class Speaker(metaclass=ABCMeta):
    @abstractmethod
    def say(self, message: str):
        raise NotImplementedError()


class GoogleSpeaker(Speaker):
    def say(self, message: str):
        mp3_fp = BytesIO()
        tts = gTTS(message, lang="en")
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        play(AudioSegment.from_mp3(mp3_fp))


class SpeakerFactory:
    SPEAKERS = {
        "google": GoogleSpeaker,
    }

    @classmethod
    def create(cls, *args, speaker_type: str = "google", **kwargs) -> Speaker:
        if speaker_type not in cls.SPEAKERS:
            raise ValueError(f"{speaker_type} is invalid")

        return cls.SPEAKERS[speaker_type](*args, **kwargs)
