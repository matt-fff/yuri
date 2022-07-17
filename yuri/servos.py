import time
import board
import busio
import asyncio
import math
import random

from typing import List
from dataclasses import dataclass

from loguru import logger
from adafruit_motor.servo import Servo
from adafruit_servokit import ServoKit
from adafruit_pca9685 import PCA9685

from yuri.config import Config
from yuri.input import Input

async def move(servo: Servo, target_angle: float, smoothing_factor: float = 0.80):
    # Keep iterating until the target angle's reached
    while not math.isclose(servo.angle, target_angle, rel_tol=0.02):
        current_angle = servo.angle
        smoothed_angle = (target_angle * smoothing_factor) + (current_angle * (1.0 - smoothing_factor))

        # Don't move onto the next smooth target until the current angle is achieved.
        servo.angle = smoothed_angle
        await asyncio.sleep(0.02)

@dataclass
class Eyes:
    upper_lids: Servo
    lower_lids: Servo
    
    left_y: Servo
    left_x: Servo

    right_y: Servo
    right_x: Servo

    @property
    def servos(self) -> List[Servo]:
        return [
            self.upper_lids,
            self.lower_lids,
            self.left_y,
            self.left_x,
            self.right_y,
            self.right_x,
        ]

    def init(self, config: Config):
        # Set everything to neutral
        for servo in self.servos:
            servo.angle = 0.5 * servo.actuation_range

        if config.left_eye.neutral_x is not None:
            self.left_x.angle = config.left_eye.neutral_x
        if config.left_eye.neutral_y is not None:
            self.left_y.angle = config.left_eye.neutral_y
        if config.right_eye.neutral_x is not None:
            self.right_x.angle = config.right_eye.neutral_x
        if config.right_eye.neutral_y is not None:
            self.right_y.angle = config.right_eye.neutral_y
    
    def calibrate(self, inputs: Input, config: Config):
        asyncio.run(self.open(True))
        for eye in ("left", "right"):
            logger.info(f"calibrate {eye} eye")
            y = getattr(self, f"{eye}_y")
            x = getattr(self, f"{eye}_x")
            incr = 3

            while inputs.button.value:
                logger.info(f"x:{x.angle:.2f} | y:{y.angle:.2f}")
                if not inputs.joyup.value:
                    y.angle = min(y.angle + incr, y.actuation_range)
                if not inputs.joydown.value:
                    y.angle = max(y.angle - incr, 0)
                if not inputs.joyleft.value:
                    x.angle = max(x.angle - incr, 0)
                if not inputs.joyright.value:
                    x.angle = min(x.angle + incr, x.actuation_range)

                time.sleep(0.3)
            config_eye = getattr(config, f"{eye}_eye")
            config_eye.neutral_x = x.angle
            config_eye.neutral_y = y.angle
            logger.info(f"Done calibrating {eye} eye")

            time.sleep(1.5)


    async def open(self, wide: bool = False):
        await asyncio.gather(
            move(self.lower_lids, 15 if wide else 13),
            move(self.upper_lids, 12 if wide else 10),
        )

    async def close(self):
        await asyncio.gather(
            move(self.lower_lids, 10.0),
            move(self.upper_lids, 7.0),
        )

    
    async def blink_loop(self):

        while True:
            await self.close()
            await self.open(wide=True)
            await self.open()
            await asyncio.sleep(random.random() * 3.0)

    async def look(self):
        """
        UP
        self.right_y = 0
        self.left_y = 180

        DOWN
        self.right_y = 180
        self.left_y = 0

        RIGHT 
        self.right_x = 0
        self.left_x = 0

        LEFT
        self.right_x = 180
        self.left_x = 180

        """


        await asyncio.gather(
            move(self.lower_lids, 10.0),
            move(self.upper_lids, 7.0),
        )



class Servos:
    def __init__(self, config: Config):
        self.config = config
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.pca = PCA9685(self.i2c)
        self.pca.frequency = 100

        self.eyes = Eyes(
            lower_lids=Servo(self.pca.channels[0], actuation_range=30),
            right_y=Servo(self.pca.channels[1], actuation_range=180),
            right_x=Servo(self.pca.channels[2], actuation_range=180), 
            
            upper_lids=Servo(self.pca.channels[4], actuation_range=30),
            left_y=Servo(self.pca.channels[5], actuation_range=180),
            left_x=Servo(self.pca.channels[6], actuation_range=180),
        )
        self.eyes.init(self.config)

    def rotate(self):
        logger.info("triggering servos")
        breakpoint()
        # for servo in self.servos:
        #     servo.angle = 180
        #     time.sleep(1)
        #     servo.angle = 0
        #     time.sleep(1)
        logger.info("done")


