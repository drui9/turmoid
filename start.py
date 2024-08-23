from argparse import ArgumentParser
from droid import create_app, toast
from loguru import logger
import asyncio
import time
import sys
import os

# --
if __name__ == '__main__':
    logger.remove()
    fmt = "{line:4}|{level:6}|{message}"
    parser = ArgumentParser(prog='Turmoid')
    parser.add_argument('--mode', type=str, default='dev', help='Program running mode.')
    parser.add_argument('--modules', type=str, default='mod', help='Modules path.')
    # --
    args = parser.parse_args()
    if args.mode == 'live':
        toast('Production mode.')
        if not os.fork():
            logger.add('logs/turmoid.log', format=fmt)
            logger.info('Started at: {}', time.time())
            app = create_app(args.modules)
            asyncio.run(app.run())
        else:
            toast('Child started.')
    else:
        toast('Development mode.')
        logger.add(sys.stdout, format=fmt)
        app = create_app(args.modules)
        asyncio.run(app.run())

