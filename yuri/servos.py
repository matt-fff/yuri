import time
import board
import busio

from typing import List
from dataclasses import dataclass

from loguru import logger
from adafruit_motor.servo import Servo
from adafruit_servokit import ServoKit
from adafruit_pca9685 import PCA9685

from yuri.config import Config



@dataclass
class Eyes:
    upper_lids: Servo
    lower_lids: Servo
    
    left_y: Servo
    left_x: Servo

    right_y: Servo
    right_x: Servo

    def open(self, wide: bool = False):
        self.lower_lids.angle = 16 if wide else 13
        self.upper_lids.angle = 13 if wide else 10

    def close(self):
        self.lower_lids.angle = 10
        self.upper_lids.angle = 7

FAST = 0.3


class Servos:
    def __init__(self, config: Config):
        self.config = config
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.pca = PCA9685(self.i2c)
        self.pca.frequency = 100

        self.eyes = Eyes(
            lower_lids=Servo(self.pca.channels[0], actuation_range=30),
            right_y=Servo(self.pca.channels[1], actuation_range=30),
            right_x=Servo(self.pca.channels[2], actuation_range=30), 
            
            upper_lids=Servo(self.pca.channels[4], actuation_range=30),
            left_y=Servo(self.pca.channels[5], actuation_range=30),
            left_x=Servo(self.pca.channels[6], actuation_range=30),
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


    def smile(self):
        self.eye_l.throttle = FAST
        self.eye_r.throttle = FAST
        time.sleep(.001)
        self.eye_l.throttle = 0
        self.eye_r.throttle = 0
