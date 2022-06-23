import time
import board
import busio

from typing import List
from dataclasses import dataclass

from loguru import logger
from adafruit_motor import servo
from adafruit_servokit import ServoKit
from adafruit_pca9685 import PCA9685

from yuri.config import Config


@dataclass
class Servo:
    servo: servo.Servo
    min_angle: int
    max_angle: int

    @property
    def neutral_angle(self) -> int:
        return (self.max_angle + self.min_angle) / 2
    
    def max(self):
        self.servo.angle = self.max_angle

    def min(self):
        self.servo.angle = self.min_angle

    def neutral(self):
        self.servo.angle = self.neutral_angle

    @property
    def angle(self):
        return self.servo.angle


@dataclass
class Face:
    left_eye: Servo
    right_eye: Servo
    nose: Servo
    left_mouth: Servo
    right_mouth: Servo

    def smile(self):
        self.left_eye.max()
        self.right_eye.max()
        
        self.left_mouth.max()
        self.right_mouth.max()

    def frown(self):
        self.left_eye.min()
        self.right_eye.min()
        
        self.left_mouth.min()
        self.right_mouth.min()

    @property
    def servos(self) -> List[Servo]:
        return [
            self.left_eye,
            self.right_eye,
            self.nose,
            self.left_mouth,
            self.right_mouth,
        ]

    def neutral(self):
        for servo in self.servos:
            servo.neutral()

    def min(self):
        for servo in self.servos:
            servo.min()

    def max(self):
        for servo in self.servos:
            servo.max()



FAST = 0.3


class Servos:
    def __init__(self, config: Config):
        self.config = config
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.pca = PCA9685(self.i2c)
        self.pca.frequency = 50
        self.face = Face(
            left_eye=Servo(
                servo=servo.Servo(self.pca.channels[0]),
                min_angle=100,
                max_angle=30,
            ),
            right_eye=Servo(
                servo=servo.Servo(self.pca.channels[1]),
                min_angle=50,
                max_angle=150,
            ),
            nose=Servo(
                servo=servo.Servo(self.pca.channels[2]),
                min_angle=100,
                max_angle=0,
            ),
            left_mouth=Servo(
                servo=servo.Servo(self.pca.channels[3]),
                min_angle=60,
                max_angle=120,
            ),
            right_mouth=Servo(
                servo=servo.Servo(self.pca.channels[4]),
                min_angle=120,
                max_angle=60,
            ),
        )

    
        



    def rotate(self):
        logger.info("triggering servos")
        breakpoint()
        # for servo in self.servos:
        #     servo.angle = 180
        #     time.sleep(1)
        #     servo.angle = 0
        #     time.sleep(1)
        logger.info("done")

    def pulse(self, servo: servo.ContinuousServo, seconds=0.001, speed=FAST):
        servo.throttle = speed
        time.sleep(seconds)
        servo.throttle = 0


    def smile(self):
        self.eye_l.throttle = FAST
        self.eye_r.throttle = FAST
        time.sleep(.001)
        self.eye_l.throttle = 0
        self.eye_r.throttle = 0
