import logging

def getlogger(name,filepath):
    logger = logging.getLogger(name)
    #logger.setLevel(logging.INFO)  各个模块单独设置日志级别
    logger.propagate = False #阻止信息上传至父
    handler = logging.FileHandler(filepath)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt="%(asctime)s [%(name)s %(funcName)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger