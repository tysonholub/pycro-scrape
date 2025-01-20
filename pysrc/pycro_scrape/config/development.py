import logging
import sys

from pycro_scrape.config.production import ProdSettings


class DevSettings(ProdSettings):
    """Development should inherit from production. Any development specific settings not passed in via the env should
    override Production
    """

    def __init__(self):
        super().__init__()
        logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, force=True, format=self.LOGGING_FORMAT)

    @property
    def environment(self) -> str:
        return "development"


settings = DevSettings()
