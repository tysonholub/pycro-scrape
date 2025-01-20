from pycro_scrape.config.production import ProdSettings


class StagingSettings(ProdSettings):
    """Staging should inherit from production. Any staging specific settings not passed in via the env should
    override Production
    """

    @property
    def environment(self) -> str:
        return "staging"


settings = StagingSettings()
