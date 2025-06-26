
from loguru import logger
import os

os.makedirs("logs", exist_ok=True)

logger.add("logs/app.log", rotation="1 week",
           retention="1 month", level="DEBUG")
