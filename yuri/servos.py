from datetime import datetime, timedelta
from abc import abstractmethod, ABCMeta
import board
import busio
import asyncio
import math
import random

from typing import List, Optional
from dataclasses import dataclass

from loguru import logger
from adafruit_motor.servo import Servo
from adafruit_pca9685 import PCA9685

from yuri.speaker import FakeSpeaker, Speaker
from yuri.config import Config, EyesConfig
from yuri.input import Input

MOVE_TIMEOUT = timedelta(seconds=1)


def set_angle(servo: Servo, target_angle: Optional[float] = None):
    if target_angle is None:
        target_angle = servo.angle

    servo.angle = max(min(target_angle, servo.actuation_range), 0)


async def move(
    servo: Servo, target_angle: float, smoothing_factor: float = 0.80
):
    start_time = datetime.utcnow()
    target_angle = max(min(target_angle, servo.actuation_range), 0)

    # Keep iterating until the target angle's reached
    while not math.isclose(servo.angle, target_angle, rel_tol=0.02):
        last_angle = servo.angle
        smoothed_angle = (target_angle * smoothing_factor) + (
            last_angle * (1.0 - smoothing_factor)
        )

        set_angle(servo, smoothed_angle)
        await asyncio.sleep(0.02)

        # Bail if there's not enough movement or a timeout
        if (
            math.isclose(servo.angle, last_angle, rel_tol=0.02)
            or datetime.utcnow() - start_time > MOVE_TIMEOUT
        ):
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

    def lid_offset(
        self,
        new_left: Optional[float] = None,
        new_right: Optional[float] = None,
    ) -> float:
        left_offset = self.eye_y_offset("left", new_angle=new_left)
        right_offset = self.eye_y_offset("right", new_angle=new_right)

        logger.debug(f"leftoff:{left_offset} rightoff:{right_offset}")
        return ((left_offset - right_offset) / 2.0) * 0.8

    def eye_y_offset(
        self, eye: str, new_angle: Optional[float] = None
    ) -> float:
        servo = getattr(self, f"{eye}_y")
        config = getattr(self.config, f"{eye}_eye")

        return (new_angle or servo.angle) - (
            config.neutral_y or (servo.actuation_range * 0.5)
        )

    def init(self):
        if self.config.left_eye.neutral_x is not None:
            set_angle(self.left_x, self.config.left_eye.neutral_x)
        if self.config.left_eye.neutral_y is not None:
            set_angle(self.left_y, self.config.left_eye.neutral_y)
        if self.config.right_eye.neutral_x is not None:
            set_angle(self.right_x, self.config.right_eye.neutral_x)
        if self.config.right_eye.neutral_y is not None:
            set_angle(self.right_y, self.config.right_eye.neutral_y)

    async def calibrate(
        self,
        inputs: Input,
        speaker: Speaker = FakeSpeaker(),
        helpers: bool = True,
    ):
        await speaker.say("run calibration")

        if helpers:
            await self.open(True)
        incr = 3
        for eye in ("left", "right"):
            await speaker.say(f"calibrate {eye} eye")
            y = getattr(self, f"{eye}_y")
            x = getattr(self, f"{eye}_x")

            skip = False
            while inputs.button.value and not skip:
                if random.random() > 0.8:
                    logger.info(f"x:{x.angle:.2f} | y:{y.angle:.2f}")
                if not inputs.joyup.value:
                    set_angle(y, y.angle + incr)
                if not inputs.joydown.value:
                    set_angle(y, y.angle - incr)
                if not inputs.joyleft.value:
                    set_angle(x, x.angle - incr)
                if not inputs.joyright.value:
                    set_angle(x, x.angle + incr)
                if not inputs.joyselect.value:
                    skip = True

                await asyncio.sleep(0.1)

            if not skip:
                config_eye = getattr(self.config, f"{eye}_eye")
                config_eye.neutral_x = x.angle
                config_eye.neutral_y = y.angle
            logger.info(f"Done calibrating {eye} eye")

            await asyncio.sleep(1.5)

        for lid in ("upper", "lower"):
            lid_servo = getattr(self, f"{lid}_lids")
            lid_config = getattr(self.config, f"{lid}_lids")
            await speaker.say(f"calibrate {lid} eyelids")

            for angle_type, prep_func in (
                ("closed_y", self.close()),
                ("wide_open_y", self.open(True)),
                ("open_y", self.open()),
            ):
                logger.info(f"calibrate {lid} eyelids {angle_type}")

                if helpers:
                    await prep_func

                skip = False
                while inputs.button.value and not skip:
                    if random.random() > 0.8:
                        logger.info(f"lid_servo:{lid_servo.angle:.2f}")
                    if not inputs.joyup.value:
                        set_angle(lid_servo, lid_servo.angle + incr)
                    if not inputs.joydown.value:
                        set_angle(lid_servo, lid_servo.angle - incr)
                    if not inputs.joyselect.value:
                        skip = True

                    await asyncio.sleep(0.1)
                if not skip:
                    setattr(lid_config, angle_type, lid_servo.angle)
                logger.info(f"Done calibrating {lid} eyelids {angle_type}")
                await asyncio.sleep(1)

        await speaker.say("done with calibration")

    async def open(self, wide: bool = False):
        await asyncio.gather(
            move(
                self.lower_lids,
                self.config.lower_lids.wide_open_y
                if wide
                else (self.config.lower_lids.open_y - self.lid_offset()),
                smoothing_factor=self.config.lower_lids.movement_smoothing,
            ),
            move(
                self.upper_lids,
                self.config.upper_lids.wide_open_y
                if wide
                else (self.config.upper_lids.open_y + self.lid_offset()),
                smoothing_factor=self.config.upper_lids.movement_smoothing,
            ),
        )

    async def close(self):
        await asyncio.gather(
            move(
                self.lower_lids,
                self.config.lower_lids.closed_y,
                smoothing_factor=self.config.lower_lids.movement_smoothing,
            ),
            move(
                self.upper_lids,
                self.config.upper_lids.closed_y,
                smoothing_factor=self.config.upper_lids.movement_smoothing,
            ),
        )

    async def blink_loop(self):
        while True:
            await self.close()
            # if random.random() > 0.8:
            # await self.open(wide=True)
            await self.open()
            await asyncio.sleep(random.random() * 3.0)

    async def horiz_look_loop(
        self, min_offset: float = 5.0, max_offset: float = 20.0
    ):
        while True:
            offset = min_offset + (random.random() * (max_offset - min_offset))
            await self.horiz_look(offset)
            await asyncio.sleep(random.random() * 2.0)
            await self.horiz_look(-offset)
            await asyncio.sleep(random.random() * 2.0)
            self.init()
            await asyncio.sleep(random.random())

    async def vert_look_loop(
        self, min_offset: float = 5.0, max_offset: float = 15.0
    ):
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
        new_left = self.left_y.angle + offset
        new_right = self.right_y.angle - offset
        lid_offset = self.lid_offset(new_left=new_left, new_right=new_right)
        logger.debug(f"offset = {lid_offset}")

        await asyncio.gather(
            move(
                self.lower_lids,
                self.config.lower_lids.open_y - lid_offset,
                smoothing_factor=self.config.lower_lids.movement_smoothing,
            ),
            move(
                self.upper_lids,
                self.config.upper_lids.open_y + lid_offset,
                smoothing_factor=self.config.upper_lids.movement_smoothing,
            ),
            move(
                self.left_y,
                new_left,
                smoothing_factor=self.config.left_eye.movement_smoothing,
            ),
            move(
                self.right_y,
                new_right,
                smoothing_factor=self.config.right_eye.movement_smoothing,
            ),
        )

    async def horiz_look(self, offset: float):
        await asyncio.gather(
            move(
                self.lower_lids,
                self.config.lower_lids.open_y - self.lid_offset(),
                smoothing_factor=self.config.lower_lids.movement_smoothing,
            ),
            move(
                self.upper_lids,
                self.config.upper_lids.open_y + self.lid_offset(),
                smoothing_factor=self.config.upper_lids.movement_smoothing,
            ),
            move(
                self.left_x,
                self.left_x.angle + offset,
                smoothing_factor=self.config.left_eye.movement_smoothing,
            ),
            move(
                self.right_x,
                self.right_x.angle + offset,
                smoothing_factor=self.config.right_eye.movement_smoothing,
            ),
        )


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

        self.eyes = Eyes(
            config=self.config.eyes,
            lower_lids=Servo(pca.channels[0]),
            right_y=Servo(pca.channels[1]),
            right_x=Servo(pca.channels[2]),
            upper_lids=Servo(pca.channels[4]),
            left_y=Servo(pca.channels[5]),
            left_x=Servo(pca.channels[6]),
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

    def rotate(self):
        logger.info("triggering servos")
        breakpoint()
        # for servo in self.servos:
        #     servo.angle = 180
        #     time.sleep(1)
        #     servo.angle = 0
        #     time.sleep(1)
        logger.info("done")




class ServosFactory:
    @classmethod
    def create(cls, config: Config) -> Servos:
        try:
            return PCA9685Servos(config)
        except ValueError:
            logger.warning("Failed to initialize servos.")
            return FakeServos(config)




