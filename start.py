from autogram import Autogram, Start
from dotenv import load_dotenv
from droid import create_app
import os

CONFIG_PATH = 'secrets/turmoid.json'

def main():
    @Start(config_file=CONFIG_PATH)
    def launch(config):
        print(config)
        app = create_app()
        app.run()

if __name__ == '__main__':
    load_dotenv()
    if os.getenv('MODE', 'dev') == 'dev':
        main()
    elif not (child := os.fork()):
        main()
