import logging
import os
import sys
from pathlib import Path

class WhatsAppTracker:
    def __init__(self, config):
        self.config = config
        self.sent_count = 0
        self._setup_logging()
        self._ensure_files_exist()

    def _setup_logging(self):
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        if not os.path.isfile(self.config['log_file']):
            with open(self.config['log_file'], 'w'):
                pass

        # File handler (UTF-8)
        file_handler = logging.FileHandler(self.config['log_file'], encoding='utf-8')
        file_handler.setFormatter(formatter)

        # Console handler with UTF-8 support
        import io
        import sys
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        self.logger = logging.getLogger('tracker')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def _ensure_files_exist(self):
        Path(self.config['sent_numbers_file']).touch()
        Path(self.config['error_numbers_file']).touch()

    def record_success(self, name, number):
        self.sent_count += 1
        self.logger.info(f"SUCCESS (#{self.sent_count}): {name} ({number})")
        with open(self.config['sent_numbers_file'], 'a') as f:
            f.write(f"{number}\n")

    def record_failure(self, name, number, error):
        self.logger.error(f"FAILED: {name} ({number}) - {error}")
        with open(self.config['error_numbers_file'], 'a') as f:
            f.write(f"{number}|{error}\n")

    def get_excluded_numbers(self):
        try:
            with open(self.config['exclude_file'], 'r') as f:
                return {line.strip() for line in f if line.strip()}
        except FileNotFoundError:
            return set()

    def get_already_sent(self):
        try:
            with open(self.config['sent_numbers_file'], 'r') as f:
                return {line.strip() for line in f if line.strip()}
        except FileNotFoundError:
            return set()