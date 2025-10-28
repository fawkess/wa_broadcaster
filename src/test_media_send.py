#!/usr/bin/env python3
"""
Test script for media attachment debugging
This bypasses the interactive prompts to test media sending directly
"""
import sys
import os
from messenger import WhatsAppMessenger

def test_media_send():
    print("=== Media Send Test Script ===\n")

    # Configuration
    chrome_user_data = "/tmp/WhatsAppSession/Session1"
    media_file = "config/media/sample.jpeg"

    # Get test details from command line or use defaults
    if len(sys.argv) >= 3:
        test_number = sys.argv[1]
        test_caption = sys.argv[2]
    else:
        print("Usage: python3 test_media_send.py <phone_number> <caption>")
        print("Example: python3 test_media_send.py 1234567890 'Hello World'")
        sys.exit(1)

    # Validate media file
    if not os.path.exists(media_file):
        print(f"ERROR: Media file not found: {media_file}")
        sys.exit(1)

    abs_media_path = os.path.abspath(media_file)
    file_size_mb = os.path.getsize(media_file) / (1024 * 1024)

    print(f"Test Configuration:")
    print(f"  Phone Number: {test_number}")
    print(f"  Caption: {test_caption}")
    print(f"  Media File: {abs_media_path}")
    print(f"  File Size: {file_size_mb:.2f}MB")
    print(f"  Chrome Profile: {chrome_user_data}")
    print()

    # Initialize messenger
    print("Initializing WhatsApp Messenger...")
    messenger = WhatsAppMessenger(chrome_user_data)

    # Login
    print("Opening WhatsApp Web...")
    if not messenger.login():
        print("\n⚠️  QR Code scan required!")
        print("Please scan the QR code in the browser window, then press Enter...")
        input()
    else:
        print("✓ Already logged in")

    print("\n" + "="*50)
    print("Starting media send with DEBUG output:")
    print("="*50 + "\n")

    # Send media with caption
    result = messenger.send_media_with_caption(test_number, media_file, test_caption)

    print("\n" + "="*50)
    print("RESULT:")
    print("="*50)

    if result is True:
        print("✓ SUCCESS: Media sent successfully!")
    else:
        print(f"✗ FAILED: {result}")

    print("\nClosing browser...")
    messenger.quit()
    print("Done.")

if __name__ == "__main__":
    test_media_send()
