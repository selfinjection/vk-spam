from loguru import logger

class Log:
    def __init__(self):
        logger = logger.add("file_{time}.log")


    def init(self):
        return self.logger