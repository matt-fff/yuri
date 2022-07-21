from typing import Optional
from aitextgen import aitextgen
from yuri.config import Config

# Without any parameters, aitextgen() will download, cache, and load the 124M GPT-2 "small" model
# ai = aitextgen()

# ai.generate()
# ai.generate(n=3, max_length=100)
# ai.generate(n=3, prompt="I believe in unicorns because", max_length=100)
# ai.generate_to_file(n=10, prompt="I believe in unicorns because", max_length=100, temperature=1.2)


class TextGen:
    def __init__(self, config: Config):
        self.config = config
        self.ai = aitextgen()

    def generate(self, prompt: Optional[str] = None):
        return self.ai.generate(prompt=prompt)
