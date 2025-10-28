import sys
import os
import pandas as pd
from messenger import WhatsAppMessenger
from tracker import WhatsAppTracker
import time
import json
import argparse

from lib import random_sleep, normalize_phone

__version__ = "1.6.0"

class WhatsAppOrchestrator:
    def __init__(self, config_path):
        self.config = self._load_config(config_path)
        self.tracker = WhatsAppTracker(self.config)
        self.messenger = WhatsAppMessenger(self.config['chrome_user_data'])
        self.message = self._load_message()

        # Media settings
        self.send_as_media = self.config.get('send_as_media', False)
        self.media_file = self.config.get('media_file', None)

        # Validate media configuration if enabled
        if self.send_as_media:
            if not self.media_file:
                print("ERROR: send_as_media is true but media_file not specified in config.json")
                sys.exit(1)

            if not os.path.exists(self.media_file):
                print(f"ERROR: Media file not found: {self.media_file}")
                print("Please check:")
                print("  1. File path is correct in config.json")
                print("  2. File exists at the specified location")
                sys.exit(1)

            # Check file size (WhatsApp typically limits to 64MB)
            file_size_mb = os.path.getsize(self.media_file) / (1024 * 1024)
            if file_size_mb > 64:
                print(f"ERROR: Media file too large: {file_size_mb:.2f}MB (max 64MB)")
                sys.exit(1)

            # Check file extension
            ext = os.path.splitext(self.media_file)[1].lower()
            allowed_exts = ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.3gp', '.pdf', '.docx', '.doc', '.txt', '.xlsx']
            if ext not in allowed_exts:
                print(f"ERROR: Unsupported media format: {ext}")
                print(f"Allowed formats: {', '.join(allowed_exts)}")
                sys.exit(1)

            print(f"✓ Media file validated: {self.media_file} ({file_size_mb:.2f}MB)")
            print(f"✓ Media mode enabled - will send media with caption")

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

        # Send test message (with or without media)
        if self.send_as_media:
            result = self.messenger.send_media_with_caption(ph_num, self.media_file, message_to_send)
        else:
            result = self.messenger.send_exact_message(ph_num, message_to_send)

        print('Verify the message sent to your phone number and confirm.')
        print('Also check if your config file is correct.')
        response = input('Input "Yes" if message is fine, else input "No" to cancel: ')
        if response.strip().upper() != 'YES':
            print(f'Cancelled by user (response: {response})')
            sys.exit(-1)

        print(f'\n✓ Test message confirmed! Starting bulk send...')
        print(f'Total contacts loaded: {len(contacts)}')
        print(f'Excluded numbers: {len(excluded)}')
        print(f'Already sent: {len(sent)}')
        print(f'Will process: {len([n for n, num, nn in contacts if normalize_phone(num) not in excluded and normalize_phone(num) not in sent])} messages\n')

        for name, number, nick_name in contacts:
            if normalize_phone(number) in excluded:
                self.tracker.logger.info(f"SKIPPED (excluded): {number}")
                continue

            if normalize_phone(number) in sent:
                self.tracker.logger.info(f"SKIPPED (already sent): {number}")
                continue

            try:
                # Replace <nick_name> placeholder with actual nick_name
                message_to_send = self.message.replace("<nick_name>", nick_name)

                # Send message (with or without media)
                if self.send_as_media:
                    result = self.messenger.send_media_with_caption(number, self.media_file, message_to_send)
                else:
                    result = self.messenger.send_exact_message(number, message_to_send)

                if result is True:
                    self.tracker.record_success(name, number)
                    self._check_timeout()
                    random_sleep(self.config['default_delay'])
                else:
                    # result contains the specific error message
                    self.tracker.record_failure(name, number, result)

                    # Critical: Stop if rate limited to avoid account ban
                    if "RATE LIMIT DETECTED" in str(result):
                        self.tracker.logger.error("⚠️ CRITICAL: Rate limit detected! Stopping to protect account.")
                        self.tracker.logger.error("⚠️ Wait at least 24 hours before resuming.")
                        break

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
