#!/usr/bin/env python3
"""
Test script with visual verification
"""
import sys
import os
import time
from messenger import WhatsAppMessenger

def test_with_verification():
    print("=== Media Send Test with Verification ===\n")

    if len(sys.argv) >= 3:
        test_number = sys.argv[1]
        test_caption = sys.argv[2]
    else:
        print("Usage: python3 test_media_with_verify.py <phone_number> <caption>")
        sys.exit(1)

    chrome_user_data = "/tmp/WhatsAppSession/Session1"
    media_file = "config/media/sample.jpeg"
    abs_media_path = os.path.abspath(media_file)

    print(f"Phone Number: {test_number}")
    print(f"Caption: {test_caption}")
    print(f"Media File: {abs_media_path}\n")

    # Initialize messenger
    print("Initializing...")
    messenger = WhatsAppMessenger(chrome_user_data)
    messenger.login()

    print("Sending media...")
    result = messenger.send_media_with_caption(test_number, media_file, test_caption)

    print("\n" + "="*60)
    print("RESULT:", result)
    print("="*60)

    if result is True:
        print("\n✓ Script reports SUCCESS")

        # Wait a bit more to ensure message is fully sent
        print("Waiting 5 more seconds for message to fully send...")
        time.sleep(5)

        # Take screenshot
        screenshot_path = "/tmp/whatsapp_after_send.png"
        messenger.driver.save_screenshot(screenshot_path)
        print(f"✓ Screenshot saved: {screenshot_path}")

        # Check if we're still on the chat page
        current_url = messenger.driver.current_url
        print(f"Current URL: {current_url}")

        # Check for any error dialogs
        page_source = messenger.driver.page_source.lower()
        error_keywords = ['error', 'failed', 'couldn\'t', 'unable', 'try again']
        found_errors = [kw for kw in error_keywords if kw in page_source]

        if found_errors:
            print(f"⚠️  Warning: Found error keywords in page: {found_errors}")
        else:
            print("✓ No error keywords found in page")

        # Check for message in chat
        if "msg-time" in messenger.driver.page_source or "_ao3e" in messenger.driver.page_source:
            print("✓ Message timestamp found in chat (message appears to be sent)")
        else:
            print("⚠️  Warning: No message timestamp found")

        print("\nKeeping browser open for 30 seconds so you can verify...")
        print("Check your WhatsApp to see if the message arrived!")
        time.sleep(30)
    else:
        print(f"\n✗ Script reports FAILURE: {result}")

    print("\nClosing browser...")
    messenger.quit()
    print("Done.")

if __name__ == "__main__":
    test_with_verification()
