import logging
import os

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Create shared logger
logger = logging.getLogger("my_package")
logger.setLevel(logging.DEBUG)

# Avoid duplicate handlers in case of multiple imports
if not logger.handlers:
    file_handler = logging.FileHandler("logs/app.log", mode="w")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)