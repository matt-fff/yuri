import time
import board
import busio

from loguru import logger
from adafruit_motor import servo
from adafruit_servokit import ServoKit
from adafruit_pca9685 import PCA9685

from yuri.config import Config

class Servos:
    def __init__(self, config: Config):
        self.config = config
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.pca = PCA9685(self.i2c)
        self.pca.frequency = 50
        self.servos = [
            servo.Servo(self.pca.channels[idx]) for idx in range(5)
        ]
        self.eye_l, self.eye_r, self.nose, self.mouth_l, self.mouth_r = self.servos

    def rotate(self):
        logger.info("triggering servos")
        for servo in self.servos:
            servo.angle = 180
            time.sleep(1)
            servo.angle = 0
            time.sleep(1)
        logger.info("done")

