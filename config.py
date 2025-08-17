import os
NEO4J_URI = "neo4j+s://55971f28.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "ZCCCayMUZPXXkNluxSeAZZxnrUstAT_co5loD2qkuRI"
LOG_FILE = os.getenv("LOG_FILE", "update.log")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "500"))