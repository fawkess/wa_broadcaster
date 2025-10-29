import sys
import os
import pandas as pd
from messenger import WhatsAppMessenger
from tracker import WhatsAppTracker
import time
import json
import argparse

from lib import random_sleep
__version__ = "1.5.1"

class WhatsAppOrchestrator:
    def __init__(self, config_path):
        self.config = self._load_config(config_path)
        self.tracker = WhatsAppTracker(self.config)
        self.messenger = WhatsAppMessenger(self.config['chrome_user_data'])
        self.message = self._load_message()

    def _load_config(self, path):
        with open(path) as f:
            return json.load(f)

    def _load_message(self):
        try:
            with open(self.config['message_file'], 'r', encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            raise Exception("Message file not found")

    def _get_contacts(self):
        df = pd.read_excel(self.config['excel_path'])
        contacts = []
        for _, row in df.iterrows():
            if pd.notna(row['WhatsApp Number']):
                raw_num = str(row['WhatsApp Number']).strip().replace('.0', '')
                name = str(row['Name'])
                nick_name = str(row['nick_name']) if pd.notna(row.get('nick_name')) else " "
                contacts.append((name, raw_num, nick_name))
        return contacts

    def _check_timeout(self):
        """Check and apply timeouts based on sent count"""
        sent_count = self.tracker.sent_count
        for interval, minutes in self.config['timeouts'].items():
            if sent_count > 0 and sent_count % int(interval) == 0:
                wait_min = minutes
                self.tracker.logger.info(
                    f"⏳ Applying timeout: Waiting {str(wait_min)} mins "
                    f"after {sent_count} messages"
                )
                time.sleep(wait_min * 60)

    def run(self):
        if not self.messenger.login():
            print("", flush=True)
            input("Scan QR Code then press Enter...\n\n")

        contacts = self._get_contacts()
        excluded = self.tracker.get_excluded_numbers()
        sent = self.tracker.get_already_sent()

        print("", flush=True)
        ph_num = input('Enter your phone number to send test message: ')
        nick_name = input('Enter nick_name: ')
        print('Sending test message to', ph_num, flush=True)
        random_sleep(1)

        message_to_send = self.message.replace("<nick_name>", nick_name)
        print('Message Preview:', message_to_send)
        result = self.messenger.send_exact_message(ph_num, message_to_send)

        print('Verify the message sent to your phone number and confirm.')
        print('Also check if your config file is correct.')
        response = input('Input "Yes" if message is fine, else input "No" to cancel: ')
        if response.upper() != 'YES':
            sys.exit(-1)

        for name, number, nick_name in contacts:
            if number in excluded:
                self.tracker.logger.info(f"SKIPPED (excluded): {number}")
                continue

            if number in sent:
                self.tracker.logger.info(f"SKIPPED (already sent): {number}")
                continue

            try:
                # Replace <nick_name> placeholder with actual nick_name
                message_to_send = self.message.replace("<nick_name>", nick_name)
                result = self.messenger.send_exact_message(number, message_to_send)
                if result is True:
                    self.tracker.record_success(name, number)
                    self._check_timeout()
                else:
                    self.tracker.record_failure(name, number, 'Time out')

                random_sleep(self.config['default_delay'])

            except Exception as e:
                self.tracker.logger.error(f"CRITICAL ERROR: {str(e)}")
                break

        self.messenger.quit()
        self.tracker.logger.info(
            f"COMPLETED. Total messages sent: {self.tracker.sent_count}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WhatsApp Automation Orchestrator")
    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
        help="Path to configuration JSON file (default: config.json)"
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information and exit"
    )

    args = parser.parse_args()

    if args.version:
        print(f"WhatsApp Orchestrator version {__version__}")
        sys.exit(0)

    # Change working directory to where config file is located
    config_dir = os.path.dirname(os.path.abspath(args.config))
    if config_dir:
        os.chdir(config_dir)
        print(f"Changed working directory to: {config_dir}")

    print(f"=== Starting script (version {__version__}) ===")
    orchestrator = WhatsAppOrchestrator(os.path.abspath(args.config))
    orchestrator.run()
