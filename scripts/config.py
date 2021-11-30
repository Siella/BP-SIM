import configparser

config = configparser.ConfigParser()
config.read('config.ini')
path_to_file = config['Data']['path_to_file']
