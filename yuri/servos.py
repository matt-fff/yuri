import time
from datetime import datetime, timedelta
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

from yuri.config import Config, EyesConfig
from yuri.input import Input

MOVE_TIMEOUT = timedelta(seconds=3)

async def move(servo: Servo, target_angle: float, smoothing_factor: float = 0.80):
    start_time = datetime.utcnow()

    # Keep iterating until the target angle's reached
    while not math.isclose(servo.angle, target_angle, rel_tol=0.02):
        current_angle = servo.angle
        smoothed_angle = (target_angle * smoothing_factor) + (current_angle * (1.0 - smoothing_factor))

        servo.angle = max(min(smoothed_angle, servo.actuation_range), 0)
        await asyncio.sleep(0.02)

        if datetime.utcnow() - start_time > MOVE_TIMEOUT:
            break


@dataclass
class Eyes:
    config: EyesConfig

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


    def init(self):

        if self.config.left_eye.neutral_x is not None:
            self.left_x.angle = self.config.left_eye.neutral_x
        if self.config.left_eye.neutral_y is not None:
            self.left_y.angle = self.config.left_eye.neutral_y
        if self.config.right_eye.neutral_x is not None:
            self.right_x.angle = self.config.right_eye.neutral_x
        if self.config.right_eye.neutral_y is not None:
            self.right_y.angle = self.config.right_eye.neutral_y

        # Set everything to neutral if its out of range
        for servo in self.servos:
            if 0.0 <= servo.angle <= servo.actuation_range:
                continue
            servo.angle = 0.5 * servo.actuation_range
    
    def calibrate(self, inputs: Input):
        logger.info("run calibration")
        asyncio.run(self.open(True))
        incr = 3
        for eye in ("left", "right"):
            logger.info(f"calibrate {eye} eye")
            y = getattr(self, f"{eye}_y")
            x = getattr(self, f"{eye}_x")

            skip = False
            while inputs.button.value and not skip:
                if random.random() > .8:
                    logger.info(f"x:{x.angle:.2f} | y:{y.angle:.2f}")
                if not inputs.joyup.value:
                    y.angle = min(y.angle + incr, y.actuation_range)
                if not inputs.joydown.value:
                    y.angle = max(y.angle - incr, 0)
                if not inputs.joyleft.value:
                    x.angle = max(x.angle - incr, 0)
                if not inputs.joyright.value:
                    x.angle = min(x.angle + incr, x.actuation_range)
                if not inputs.joyselect.value:
                    skip = True

                time.sleep(0.1)

            if not skip:
                config_eye = getattr(self.config, f"{eye}_eye")
                config_eye.neutral_x = x.angle
                config_eye.neutral_y = y.angle
            logger.info(f"Done calibrating {eye} eye")

            time.sleep(1.5)

        logger.info("closed position")

        for lid in ("upper", "lower"):
            lid_servo = getattr(self, f"{lid}_lids")
            lid_config = getattr(self.config, f"{lid}_lids")

            for angle_type, prep_func in (
                ("closed_y", self.close()),
                ("wide_open_y",self.open(True)),
                ("open_y",self.open()),
            ):
                logger.info(f"calibrate {lid} eyelids {angle_type}")
                asyncio.run(prep_func)

                skip = False
                while inputs.button.value and not skip:
                    if random.random() > .8:
                        logger.info(f"lid_servo:{lid_servo.angle:.2f}")
                    if not inputs.joyup.value:
                        lid_servo.angle = min(lid_servo.angle + incr, lid_servo.actuation_range)
                    if not inputs.joydown.value:
                        lid_servo.angle = max(lid_servo.angle - incr, 0)

                    if not inputs.joyselect.value:
                        skip = True

                    time.sleep(0.1)
                if not skip:
                    setattr(lid_config, angle_type, lid_servo.angle)
                logger.info(f"Done calibrating {lid} eyelids {angle_type}")
                time.sleep(1)



    async def open(self, wide: bool = False):
        await asyncio.gather(
            move(
                self.lower_lids,
                self.config.lower_lids.wide_open_y if wide else self.config.lower_lids.open_y,
                smoothing_factor=self.config.lower_lids.movement_smoothing
            ),
            move(
                self.upper_lids,
                self.config.upper_lids.wide_open_y if wide else self.config.upper_lids.open_y,
                smoothing_factor=self.config.upper_lids.movement_smoothing
            ),
        )

    async def close(self):
        await asyncio.gather(
            move(
                self.lower_lids,
                self.config.lower_lids.closed_y,
                smoothing_factor=self.config.lower_lids.movement_smoothing
            ),
            move(
                self.upper_lids,
                self.config.upper_lids.closed_y,
                smoothing_factor=self.config.upper_lids.movement_smoothing
            ),
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
            move(
                self.left_y,
                self.left_y.angle + offset,
                smoothing_factor=self.config.left_eye.movement_smoothing
            ),
            move(
                self.right_y,
                self.right_y.angle - offset,
                smoothing_factor=self.config.right_eye.movement_smoothing
            ),
        )

    async def horiz_look(self, offset: float):
        await asyncio.gather(
            move(
                self.left_x,
                self.left_x.angle + offset,
                smoothing_factor=self.config.left_eye.movement_smoothing
            ),
            move(
                self.right_x,
                self.right_x.angle - offset,
                smoothing_factor=self.config.right_eye.movement_smoothing
            ),
        )
    

class Servos:
    def __init__(self, config: Config):
        i2c = busio.I2C(board.SCL, board.SDA)
        pca = PCA9685(i2c)
        pca.frequency = 100

        self.eyes = Eyes(
            config=config.eyes,
            lower_lids=Servo(pca.channels[0]),
            right_y=Servo(pca.channels[1]),
            right_x=Servo(pca.channels[2]), 
            
            upper_lids=Servo(pca.channels[4]),
            left_y=Servo(pca.channels[5]),
            left_x=Servo(pca.channels[6]),
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


