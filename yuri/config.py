from dataclasses import field
from pydantic.dataclasses import dataclass
from pydantic import BaseModel

import board
import json
from typing import Optional
from loguru import logger

Pin = board.pin.Pin

class PinsConfig(BaseModel):
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


class EyeConfig(BaseModel):
    neutral_x: Optional[float] = None
    neutral_y: Optional[float] = None
    movement_smoothing: float = 0.80

class LidsConfig(BaseModel):
    closed_y: float
    open_y: float
    wide_open_y: float
    movement_smoothing: float = 0.80

class EyesConfig(BaseModel):
    left_eye: EyeConfig = EyeConfig()
    right_eye: EyeConfig = EyeConfig()
    upper_lids: LidsConfig = LidsConfig(
        closed_y=7.0,
        open_y=10.0,
        wide_open_y=12.0,
    )
    lower_lids: LidsConfig = LidsConfig(
        closed_y=10.0,
        open_y=13.0,
        wide_open_y=15.0,
    )
    

class Config(BaseModel):
    listener_type: str = "sphinx"
    speaker_type: str = "google"
    pins: PinsConfig = PinsConfig()
    eyes: EyesConfig = EyesConfig()

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
