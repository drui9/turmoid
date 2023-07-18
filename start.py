from argparse import ArgumentParser
from loguru import logger
import arrow
import sys

def main():
    logger.remove()
    fmt = "{line:4}| [{file}:{level:6}] > {message}"
    parser = ArgumentParser(prog='Turmoid')
    parser.add_argument('--mode', type=str, default='dev', help='Program running mode.')
    parser.add_argument('--modules', type=str, default='mod', help='Modules path.')
    # --
    args = parser.parse_args()
    logger.add('logs/turmoid.log', format=fmt)
    logger.add(sys.stdout, format=fmt)
    logger.info('Started at: {}', arrow.now().humanize())
    logger.debug(args)

# --
if __name__ == '__main__':
    main()

