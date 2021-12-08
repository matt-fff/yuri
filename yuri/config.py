from dataclasses import dataclass, field

import board
import yaml
import board


@dataclass
class Pins:
    dotstar_clock: int = board.D6
    dotstar_data: int = board.D5
    button: int = board.D17
    joydown: int = board.D27
    joyleft: int = board.D22
    joyup: int = board.D23
    joyright: int = board.D24
    joyselect: int = board.D16

@dataclass
class Config:
    listener_type: str = "sphinx"
    speaker_type: str = "google"
    pins: Pins = field(default_factory=Pins)


class ConfigFactory:
    @classmethod
    def create(cls, location: str) -> Config:
        with open(location) as config_file:
            file_data = yaml.load(config_file, Loader=yaml.FullLoader)

        return Config(**(file_data or {}))
