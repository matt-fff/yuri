import asyncio
import random

from yuri.config import Config
from yuri.listener import ListenerFactory
from yuri.speaker import SpeakerFactory
from yuri.lights import Lights
from yuri.input import Input
from yuri.servos import ServosFactory


class Yuri:
    def __init__(self, config: Config):
        self.servos = ServosFactory.create(config)
        self.inputs = Input(config)
        self.lights = Lights(config)
        self.speaker = SpeakerFactory.create(config)
        self.listener = ListenerFactory.create(config)

    async def run(self):
        await asyncio.gather(
            self.servos.loop(),
            # self.lights.cycle_colors(),
            self.speech_loop(),
        )

    async def speech_loop(self):
        while True:
            await self.speaker.say(
                random.choice(["hmm", "interesting", "where am I?"])
            )
            await asyncio.sleep(random.random() * 30.0)
