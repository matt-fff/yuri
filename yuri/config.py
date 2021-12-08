from dataclasses import dataclass

import yaml


@dataclass
class Config:
    listener_type: str = "sphinx"
    speaker_type: str = "google"


class ConfigFactory:
    @classmethod
    def create(cls, location: str) -> Config:
        with open(location) as config_file:
            file_data = yaml.load(config_file, Loader=yaml.FullLoader)

        return Config(**(file_data or {}))
