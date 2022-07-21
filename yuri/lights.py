import time
import adafruit_dotstar
from datetime import datetime, timedelta
from loguru import logger

from yuri.config import Config


class Lights:
    def __init__(self, config: Config):
        self.config = config
        self.dots = adafruit_dotstar.DotStar(
            config.pins.dotstar_clock, config.pins.dotstar_data, 3, brightness=0.2
        )

    @staticmethod
    def wheel(pos):
        # Input a value 0 to 255 to get a color value.
        # The colours are a transition r - g - b - back to r.
        if pos < 0 or pos > 255:
            return (0, 0, 0)
        if pos < 85:
            return (255 - pos * 3, pos * 3, 0)
        if pos < 170:
            pos -= 85
            return (0, 255 - pos * 3, pos * 3)
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)

    def off(self):
        for i in range(3):
            self.dots[i] = 0

    def cycle_colors(self, seconds: int):
        stop_at = datetime.utcnow() + timedelta(seconds=seconds)
        logger.info("cycle_colors.start")

        while datetime.utcnow() < stop_at:
            for j in range(255):
                for i in range(3):
                    rc_index = (i * 256 // 3) + j * 5
                    self.dots[i] = self.wheel(rc_index & 255)
                self.dots.show()
                time.sleep(0.01)

        self.off()
        logger.info("cycle_colors.done")
