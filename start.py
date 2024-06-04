from dotenv import load_dotenv
from droid import create_app
import os

if __name__ == '__main__':
    load_dotenv()
    if os.getenv('MODE', 'dev') == 'dev':
        app = create_app()
        app.run()
    elif not (child := os.fork()):
        app = create_app()
        app.run()
