from dataclasses import field
from pydantic.dataclasses import dataclass
from pydantic import BaseModel

import board
import json
from typing import Optional
from loguru import logger

Pin = board.pin.Pin

class Pins(BaseModel):
    dotstar_clock: Pin = board.D6
    dotstar_data: Pin = board.D5
    button: Pin = board.D17
    joydown: Pin = board.D27
    joyleft: Pin = board.D22
    joyup: Pin = board.D23
    joyright: Pin = board.D24
    joyselect: Pin = board.D16
    
    class Config:
        arbitrary_types_allowed = True


class Eye(BaseModel):
    neutral_x: Optional[float] = None
    neutral_y: Optional[float] = None

class Config(BaseModel):
    listener_type: str = "sphinx"
    speaker_type: str = "google"
    pins: Pins = Pins()
    left_eye: Eye = Eye()
    right_eye: Eye = Eye()
    eyelid_movement_smoothing: float = 0.80
    eyeball_movement_smoothing: float = 0.80

    def save(self, location: str):
        with open(location, "w") as config_file:
            config_file.write(json.dumps(self.dict(exclude={"pins"}), indent=2))



class ConfigFactory:
    @classmethod
    def create(cls, location: str) -> Config:
        with open(location) as config_file:
            obj = {}
            try:
                obj = json.loads(config_file.read())
            except json.JSONDecodeError:
                logger.warning("error parsing config")

            config = Config.parse_obj(obj) 


        return config
