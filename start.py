from argparse import ArgumentParser
from droid import create_app
from loguru import logger
import asyncio
import os

# --
if __name__ == '__main__':
    parser = ArgumentParser(prog='Turmoid')
    parser.add_argument('--mode', type=str, default='dev', help='Program running mode.')
    try:
        args = parser.parse_args()
        if args.mode == 'live':
            if not os.fork():
                logger.remove()
                logger.add('Logs/turmoid.log')
                logger.info('Turmoid deployed.')
                app = create_app()
                asyncio.run(app.run())
            else:
                logger.debug('Child started.')
        else:
            app = create_app()
            asyncio.run(app.run())
    except TimeoutError:
        logger.critical('Another instance is running!')

