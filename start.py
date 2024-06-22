from droid import create_app
from autogram import Start
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
    main()
