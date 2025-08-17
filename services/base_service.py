from utils.logger import LogWriter

class BaseService:
    def __init__(self, client, logger: LogWriter, dry_run: bool):
        self.client = client
        self.log = logger
        self.dry_run = dry_run
