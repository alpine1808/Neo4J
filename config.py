import os
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
LOG_FILE = os.getenv("LOG_FILE", "update.log")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "500"))