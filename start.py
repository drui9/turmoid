from droid import create_app
from loguru import logger

# --
if __name__ == '__main__':
    try:
        app = create_app()
        app.run()
    except TimeoutError:
        logger.critical('Another instance is running!')

