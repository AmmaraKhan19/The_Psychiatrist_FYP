### This is a helper library for app that allows managing trivial or recurring tasks

import logging
import yaml

# set loggers
helper_logger = logging.getLogger("helper")
app_logger = logging.getLogger("app")
db_logger = logging.getLogger("db")
background_logger = logging.getLogger("background")
#config variables
path_to_config = "./project/configs/config.yaml"
config = {}

# loads the config file
try:
    with open(path_to_config) as file:
        config = yaml.safe_load(file)
    if config == {}:
        raise
except:
    helper_logger.error("Unable to load config file!")
    exit()

if config['logging'] == "DEBUG":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
elif config['logging'] == "INFO":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
elif config['logging'] == "WARNING":
    logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
elif config['logging'] == "ERROR":
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
elif config['logging'] == "CRITICAL":
    logging.basicConfig(level=logging.CRITICAL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
helper_logger.debug("Config loaded successfully!")

# provides a log when requested from main flow
def log(level,logger,message):
    try:
        if level == "debug":
            if logger == "app":
                app_logger.debug(message)
            elif logger == "db":
                db_logger.debug(message)
            elif logger == "background":
                background_logger.debug(message)
        elif level == "info":
            if logger == "app":
                app_logger.info(message)
            elif logger == "db":
                db_logger.debug(message)
            elif logger == "background":
                background_logger.debug(message)
        elif level == "warning":
            if logger == "app":
                app_logger.warning(message)
            elif logger == "db":
                db_logger.debug(message)
            elif logger == "background":
                background_logger.debug(message)
        elif level == "error":
            if logger == "app":
                app_logger.error(message)
            elif logger == "db":
                db_logger.debug(message)
            elif logger == "background":
                background_logger.debug(message)
        elif level == "critical":
            if logger == "app":
                app_logger.critical(message)
            elif logger == "db":
                db_logger.debug(message)
            elif logger == "background":
                background_logger.debug(message)
        else:
            raise
    except:
        helper_logger.error("Logging Issue")
    return True