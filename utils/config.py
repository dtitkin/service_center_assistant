from pathlib import Path
import configparser

_conf_folder = Path(__file__).parent.parent / "conf"


class _Setiings():
    def __init__(self):
        config = configparser.ConfigParser()
        config.read(Path(_conf_folder, 'settings.ini'))

        self.login: str = config['authorization']['login']
        self.password: str = config['authorization']['password']

        self.implicitly_wait: int = int(config['wait_time']['implicitly_wait'])
        self.until_wait: int = int(config['wait_time']['until_wait'])

        self.login_uri: str = config['uri']['login_uri']

        self.main_themes: str = config['front']['main_themes']
        self.font_window: str = config['front']['font_window']
        self.font_h1: str = config['front']['font_h1']
        self.font_table_h: str = config['front']['font_table_h']
        self.font_table_d: str = config['front']['font_table_d']


settings = _Setiings()
