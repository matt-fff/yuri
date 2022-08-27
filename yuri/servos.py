from abc import abstractmethod, ABCMeta
import board
import busio

from loguru import logger
from adafruit_motor.servo import Servo
from adafruit_pca9685 import PCA9685

from yuri.speaker import FakeSpeaker, Speaker
from yuri.config import Config
from yuri.input import Input
from yuri.eyes import Eyes

class Servos(metaclass=ABCMeta):
    def __init__(self, config: Config):
        self.config = config

    @abstractmethod
    async def loop(self):
        raise NotImplementedError()

    @abstractmethod
    async def calibrate(
        self,
        inputs: Input,
        speaker: Speaker = FakeSpeaker(),
        helpers: bool = True,
    ):
        raise NotImplementedError()



class FakeServos(Servos):
    def __init__(self, config: Config):
        super().__init__(config)

    async def loop(self):
        pass
    
    async def calibrate(
        self,
        inputs: Input,
        speaker: Speaker = FakeSpeaker(),
        helpers: bool = True,
    ):
        pass

class PCA9685Servos(Servos):
    def __init__(self, config: Config):
        super().__init__(config)

        i2c = busio.I2C(board.SCL, board.SDA)

        pca = PCA9685(i2c)
        pca.frequency = 100

        eye_kwargs = dict(
            config=self.config.eyes,
            lower_lids=Servo(pca.channels[0]),
            right_y=Servo(pca.channels[1]),
            right_x=Servo(pca.channels[2]),
            upper_lids=Servo(pca.channels[4]),
            left_y=Servo(pca.channels[5]),
            left_x=Servo(pca.channels[6]),
        )

        self.eyes = Eyes(
            **eye_kwargs
        )
        self.eyes.init()

    async def loop(self):
        await self.eyes.loop()

    async def calibrate(
        self,
        inputs: Input,
        speaker: Speaker = FakeSpeaker(),
        helpers: bool = True,
    ):
        await self.eyes.calibrate(inputs, speaker, helpers)

class ServosFactory:
    @classmethod
    def create(cls, config: Config) -> Servos:
        try:
            return PCA9685Servos(config)
        except ValueError:
            logger.warning("Failed to initialize servos.")
            return FakeServos(config)

