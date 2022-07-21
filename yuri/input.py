import time
from datetime import datetime, timedelta
from digitalio import DigitalInOut, Direction, Pull
from yuri.config import Config

from loguru import logger


class Input:
    def __init__(self, config: Config):
        self.config = config

        buttons = [
            self.config.pins.button,
            self.config.pins.joyup,
            self.config.pins.joydown,
            self.config.pins.joyleft,
            self.config.pins.joyright,
            self.config.pins.joyselect,
        ]

        for i, pin in enumerate(buttons):
            buttons[i] = DigitalInOut(pin)
            buttons[i].direction = Direction.INPUT
            buttons[i].pull = Pull.UP
        (
            self.button,
            self.joyup,
            self.joydown,
            self.joyleft,
            self.joyright,
            self.joyselect,
        ) = buttons

    def demo(self, seconds: int):
        stop_at = datetime.utcnow() + timedelta(seconds=seconds)
        logger.info("demo.start")

        while datetime.utcnow() < stop_at:
            if not self.button.value:
                logger.info("Button pressed")
            if not self.joyup.value:
                logger.info("Joystick up")
            if not self.joydown.value:
                logger.info("Joystick down")
            if not self.joyleft.value:
                logger.info("Joystick left")
            if not self.joyright.value:
                logger.info("Joystick right")
            if not self.joyselect.value:
                logger.info("Joystick select")

            time.sleep(0.1)

        logger.info("demo.done")
