import logging
import os
from logging.handlers import RotatingFileHandler
import sys

# Ensure logs directory exists
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "nova.log")

class NovaLogger:
    def __init__(self):
        self.logger = logging.getLogger("NOVA")
        self.logger.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 1. Console Handler (Stdout)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        
        # 2. File Handler (Rotating)
        # Max 5MB, 5 backups
        fh = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=5)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def get_logger(self):
        return self.logger

# Global instance
_nova_logger = NovaLogger()
logger = _nova_logger.get_logger()
