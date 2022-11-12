import logging
import atexit
import time
import sys
from logging.handlers import RotatingFileHandler

# https://docs.python.org/3/howto/logging-cookbook.html

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

#log_handler = logging.handlers.WatchedFileHandler(__file__+'f.log')
#log_handler = logging.handlers.WatchedFileHandler("test.log")
fh = RotatingFileHandler("motion.log", mode='a', maxBytes=5*1024*1024, backupCount=2, encoding=None, delay=0)
fh.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s:%(module)s:%(funcName)s:%(lineno)d - %(message)s")
#formatter.converter = time.gmtime  # if you want UTC time
fh.setFormatter(formatter)
logger.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
formatter = logging.Formatter("%(levelname)s - %(name)s:%(module)s:%(funcName)s:%(lineno)d - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

logger.info("")
logger.info("")
logger.info("------------------------- START -------------------------")

sys.excepthook = handle_exception

@atexit.register
def goodbye():
    logger.info("-------------------------- END --------------------------")

#raise RuntimeError("Test unhandled")
#for l in range(100000):
#    logger.info("Nr:" + str(l))



'''

#py1
import logging
def fun1():
    LOGGER = logging.getLogger(__name__)
    LOGGER.info('fun1 runs')

#py2
import logging
def fun2():
    LOGGER = logging.getLogger(__name__)
    LOGGER.info('fun2 runs')

#master.py
import py1
import py2
import logging
def main():
    logging.basicConfig(filename='log.log',level=logging.INFO)
    LOGGER = logging.getLogger("main")
    py1.fun1()
    py2.fun2()
    LOGGER.info('Master runs')

if __name__ == "__main__":
    main()
    
'''


'''
info
warning
error
critical
log
exception

CRITICAL
ERROR
WARNING
INFO
DEBUG
NOTSET
'''

