from autogram import Autogram, Start
from droid import create_app
import os

CONFIG_PATH = 'secrets/turmoid.json'

def main():
    app = create_app()
    # --
    @Start(config_file=CONFIG_PATH)
    def launch(config):
        app.config = config
        app.run()

if __name__ == '__main__':
    if os.getenv('MODE', 'dev') == 'dev':
        main()
    elif not (child := os.fork()):
        main()
