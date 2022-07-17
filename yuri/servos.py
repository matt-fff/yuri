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

        servo.angle = smoothed_angle
        await asyncio.sleep(0.02)

async def move_offset(servos: List[Servo], angle_offset: float, smoothing_factor: float = 0.80):

    original_angles = [servo.angle for servo in servos]

    def target_angle(idx: int) -> float:
        return original_angles[idx] + angle_offset

    def complete() -> bool:
        for idx, servo in enumerate(servos):
            if not math.isclose(servo.angle, target_angle(idx), rel_tol=0.02):
                return False
        return True

    while not complete():
        for idx, servo in enumerate(servos):
            current_angle = servo.angle
            smoothed_angle = (target_angle(idx) * smoothing_factor) + (current_angle * (1.0 - smoothing_factor))

            servo.angle = smoothed_angle
        logger.debug(f"angles: {[servo.angle for servo in servos]}")
        await asyncio.sleep(0.02)



@dataclass
class Eyes:
    config: Config

    upper_lids: Servo
    lower_lids: Servo
    
    left_y: Servo
    left_x: Servo

    right_y: Servo
    right_x: Servo


    @property
    def lid_smoothing(self):
        return self.config.eyelid_movement_smoothing

    @property
    def ball_smoothing(self):
        return self.config.eyeball_movement_smoothing

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


    def init(self):

        if self.config.left_eye.neutral_x is not None:
            self.left_x.angle = self.config.left_eye.neutral_x
        if self.config.left_eye.neutral_y is not None:
            self.left_y.angle = self.config.left_eye.neutral_y
        if self.config.right_eye.neutral_x is not None:
            self.right_x.angle = self.config.right_eye.neutral_x
        if self.config.right_eye.neutral_y is not None:
            self.right_y.angle = self.config.right_eye.neutral_y

        # Set everything to neutral
        for servo in self.servos:
            if 0.0 <= servo.angle <= servo.actuation_range:
                continue
            servo.angle = 0.5 * servo.actuation_range
    
    def calibrate(self, inputs: Input):
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
            config_eye = getattr(self.config, f"{eye}_eye")
            config_eye.neutral_x = x.angle
            config_eye.neutral_y = y.angle
            logger.info(f"Done calibrating {eye} eye")

            time.sleep(1.5)


    async def open(self, wide: bool = False):
        await asyncio.gather(
            move(self.lower_lids, 15 if wide else 13, smoothing_factor=self.lid_smoothing),
            move(self.upper_lids, 12 if wide else 10, smoothing_factor=self.lid_smoothing),
        )

    async def close(self):
        await asyncio.gather(
            move(self.lower_lids, 10.0, smoothing_factor=self.lid_smoothing),
            move(self.upper_lids, 7.0, smoothing_factor=self.lid_smoothing),
        )

    
    async def blink_loop(self):
        while True:
            await self.close()
            await self.open(wide=True)
            await self.open()
            await asyncio.sleep(random.random() * 3.0)

    async def horiz_look_loop(self, min_offset: float = 10.0, max_offset: float = 25.0):
        while True:
            offset = min_offset + (random.random() * (max_offset - min_offset))
            await self.horiz_look(offset)
            await asyncio.sleep(random.random() * 2.0)
            await self.horiz_look(-offset)
            await asyncio.sleep(random.random() * 2.0)
            self.init()
            await asyncio.sleep(random.random())

    async def vert_look_loop(self, min_offset: float = 10.0, max_offset: float = 25.0):
        while True:
            offset = min_offset + (random.random() * (max_offset - min_offset))
            await self.vert_look(offset)
            await asyncio.sleep(random.random() * 2.0)
            await self.vert_look(-offset)
            await asyncio.sleep(random.random() * 2.0)
            self.init()
            await asyncio.sleep(random.random())


    async def loop(self):
        await asyncio.gather(
            self.horiz_look_loop(),
            self.vert_look_loop(),
            self.blink_loop(),
        )

    async def vert_look(self, offset: float):
        await asyncio.gather(
            move(self.left_y, self.left_y.angle + offset, smoothing_factor=self.ball_smoothing),
            move(self.right_y, self.right_y.angle - offset, smoothing_factor=self.ball_smoothing),
        )
        await asyncio.sleep(random.random() * 2.0)
        await asyncio.gather(
            move(self.left_y, self.left_y.angle - offset, smoothing_factor=self.ball_smoothing),
            move(self.right_y, self.right_y.angle + offset, smoothing_factor=self.ball_smoothing),
        )
        await asyncio.sleep(random.random() * 2.0)

    async def horiz_look(self, offset: float):
        await move_offset([self.left_x, self.right_x], offset, smoothing_factor=self.ball_smoothing)
        await asyncio.sleep(random.random() * 2.0)
        await move_offset([self.left_x, self.right_x], -offset, smoothing_factor=self.ball_smoothing)
        await asyncio.sleep(random.random() * 2.0)
    

class Servos:
    def __init__(self, config: Config):
        i2c = busio.I2C(board.SCL, board.SDA)
        pca = PCA9685(i2c)
        pca.frequency = 100

        self.eyes = Eyes(
            config=config,
            lower_lids=Servo(pca.channels[0], actuation_range=30),
            right_y=Servo(pca.channels[1], actuation_range=180),
            right_x=Servo(pca.channels[2], actuation_range=180), 
            
            upper_lids=Servo(pca.channels[4], actuation_range=30),
            left_y=Servo(pca.channels[5], actuation_range=180),
            left_x=Servo(pca.channels[6], actuation_range=180),
        )
        self.eyes.init()

    def rotate(self):
        logger.info("triggering servos")
        breakpoint()
        # for servo in self.servos:
        #     servo.angle = 180
        #     time.sleep(1)
        #     servo.angle = 0
        #     time.sleep(1)
        logger.info("done")


