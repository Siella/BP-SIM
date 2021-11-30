import configparser
import os


def get_pardir(path: str) -> str:
    return path[:path.rfind('\\')]


parent_cwd = get_pardir(os.path.dirname(__file__))
config = configparser.ConfigParser()
config.read(os.path.join(parent_cwd, 'config.ini'))
path_to_file = config['Data']['path_to_file']
