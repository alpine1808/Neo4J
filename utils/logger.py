from datetime import datetime

class LogWriter:
    def __init__(self, log_file: str):
        self.log_file = log_file
        with open(self.log_file, "a", encoding="utf-8-sig") as f:
            f.write(f"\n===== RUN at {datetime.now().isoformat()} =====\n")
    def log(self, message: str):
        ts = datetime.now().isoformat()
        line = f"[{ts}] {message}"
        print(line)
        with open(self.log_file, "a", encoding="utf-8-sig") as f:
            f.write(line + "\n")
