#!/usr/bin/env python3
"""
Inspect send button in media preview
"""
import sys
import time
from messenger import WhatsAppMessenger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def inspect_send_button():
    print("=== Media Send Button Inspector ===\n")

    if len(sys.argv) < 2:
        print("Usage: python3 inspect_send_button.py <phone_number>")
        sys.exit(1)

    test_number = sys.argv[1]
    chrome_user_data = "/tmp/WhatsAppSession/Session1"
    media_file = "config/media/sample.jpeg"

    print(f"Phone Number: {test_number}")
    print(f"Media File: {media_file}\n")

    # Initialize messenger
    messenger = WhatsAppMessenger(chrome_user_data)
    messenger.login()

    # Navigate to chat
    print("Navigating to chat...")
    messenger.driver.get(f"https://web.whatsapp.com/send?phone={test_number}")

    # Wait for chat to load
    WebDriverWait(messenger.driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
    )
    print("✓ Chat loaded\n")

    time.sleep(2)

    # Click attach button
    print("Clicking attach button...")
    attach_btn = WebDriverWait(messenger.driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@aria-label="Attach"]'))
    )
    attach_btn.click()
    print("✓ Attach button clicked\n")

    time.sleep(2)

    # Upload file
    print("Uploading file...")
    import os
    abs_media_path = os.path.abspath(media_file)
    file_input = WebDriverWait(messenger.driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'))
    )
    file_input.send_keys(abs_media_path)
    print("✓ File uploaded\n")

    time.sleep(5)  # Wait for preview to load

    print("="*60)
    print("INSPECTING SEND BUTTON IN MEDIA PREVIEW...")
    print("="*60 + "\n")

    # JavaScript to find all possible send button elements
    js_script = """
    let results = {
        sendIcons: [],
        sendButtons: [],
        allButtonsInPreview: []
    };

    // 1. Find elements with 'send' in data-icon
    document.querySelectorAll('[data-icon]').forEach(el => {
        let icon = el.getAttribute('data-icon');
        if (icon && icon.toLowerCase().includes('send')) {
            results.sendIcons.push({
                tag: el.tagName,
                dataIcon: icon,
                ariaLabel: el.getAttribute('aria-label'),
                title: el.getAttribute('title'),
                role: el.getAttribute('role'),
                class: el.className
            });
        }
    });

    // 2. Find buttons with send-related text
    document.querySelectorAll('button, [role="button"], div[role="button"], span[role="button"]').forEach(btn => {
        let ariaLabel = (btn.getAttribute('aria-label') || '').toLowerCase();
        let title = (btn.getAttribute('title') || '').toLowerCase();
        let text = btn.textContent.toLowerCase();

        if (ariaLabel.includes('send') || title.includes('send') || text.includes('send')) {
            results.sendButtons.push({
                tag: btn.tagName,
                ariaLabel: btn.getAttribute('aria-label'),
                title: btn.getAttribute('title'),
                text: btn.textContent.substring(0, 50),
                dataIcon: btn.querySelector('[data-icon]')?.getAttribute('data-icon'),
                class: btn.className
            });
        }
    });

    // 3. Find all clickable elements in what might be the preview modal/dialog
    let modals = document.querySelectorAll('[role="dialog"], .modal, [class*="preview"], [class*="media"]');
    modals.forEach(modal => {
        modal.querySelectorAll('button, [role="button"], div[role="button"]').forEach(btn => {
            results.allButtonsInPreview.push({
                tag: btn.tagName,
                ariaLabel: btn.getAttribute('aria-label'),
                title: btn.getAttribute('title'),
                dataIcon: btn.querySelector('[data-icon]')?.getAttribute('data-icon'),
                text: btn.textContent.substring(0, 30)
            });
        });
    });

    return results;
    """

    try:
        results = messenger.driver.execute_script(js_script)

        print("1. SEND ICONS (data-icon contains 'send'):")
        if results['sendIcons']:
            for i, el in enumerate(results['sendIcons'], 1):
                print(f"   [{i}] {el['tag']} | data-icon='{el['dataIcon']}' | aria-label='{el['ariaLabel']}' | title='{el['title']}'")
        else:
            print("   None found")

        print("\n2. BUTTONS WITH 'SEND' TEXT:")
        if results['sendButtons']:
            for i, el in enumerate(results['sendButtons'], 1):
                print(f"   [{i}] {el['tag']} | aria-label='{el['ariaLabel']}' | title='{el['title']}' | data-icon='{el['dataIcon']}'")
                print(f"        text: {el['text']}")
        else:
            print("   None found")

        print("\n3. ALL BUTTONS IN PREVIEW MODAL/DIALOG:")
        if results['allButtonsInPreview']:
            print(f"   Found {len(results['allButtonsInPreview'])} buttons:")
            for i, el in enumerate(results['allButtonsInPreview'], 1):
                print(f"   [{i}] {el['tag']} | aria-label='{el['ariaLabel']}' | data-icon='{el['dataIcon']}' | text='{el['text']}'")
        else:
            print("   No preview modal found or no buttons in it")

    except Exception as e:
        print(f"Error executing JavaScript: {e}")

    # Save page source
    print("\n" + "="*60)
    with open('/tmp/whatsapp_media_preview.html', 'w', encoding='utf-8') as f:
        f.write(messenger.driver.page_source)
    print("✓ Saved page source to: /tmp/whatsapp_media_preview.html")
    print("  Search for 'send' keywords in this file")

    print("\nClosing browser...")
    messenger.quit()
    print("Done.")

if __name__ == "__main__":
    inspect_send_button()
