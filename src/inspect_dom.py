#!/usr/bin/env python3
"""
DOM Inspector - Find current WhatsApp Web attach button selectors
"""
import sys
from messenger import WhatsAppMessenger
from selenium.webdriver.common.by import By

def inspect_dom():
    print("=== WhatsApp Web DOM Inspector ===\n")

    if len(sys.argv) < 2:
        print("Usage: python3 inspect_dom.py <phone_number>")
        sys.exit(1)

    test_number = sys.argv[1]
    chrome_user_data = "/tmp/WhatsAppSession/Session1"

    print(f"Phone Number: {test_number}")
    print(f"Chrome Profile: {chrome_user_data}\n")

    # Initialize messenger
    messenger = WhatsAppMessenger(chrome_user_data)

    # Login
    print("Opening WhatsApp Web...")
    if not messenger.login():
        print("⚠️  QR Code scan required - please scan and press Enter...")
        input()

    # Navigate to chat
    print(f"Navigating to chat with {test_number}...")
    messenger.driver.get(f"https://web.whatsapp.com/send?phone={test_number}")

    input("\nPress Enter once the chat is fully loaded...")

    print("\n" + "="*60)
    print("Searching for attach button elements...")
    print("="*60 + "\n")

    # Try to find all possible button/icon elements
    js_script = """
    // Find all elements that might be the attach button
    let results = [];

    // Look for clip icons
    let clips = document.querySelectorAll('[data-icon*="clip"], [aria-label*="ttach"], [title*="ttach"]');
    clips.forEach(el => {
        results.push({
            tag: el.tagName,
            dataIcon: el.getAttribute('data-icon'),
            ariaLabel: el.getAttribute('aria-label'),
            title: el.getAttribute('title'),
            role: el.getAttribute('role'),
            class: el.className,
            id: el.id
        });
    });

    // Look for plus icons (sometimes used for attach)
    let plus = document.querySelectorAll('[data-icon*="plus"]');
    plus.forEach(el => {
        results.push({
            tag: el.tagName,
            dataIcon: el.getAttribute('data-icon'),
            ariaLabel: el.getAttribute('aria-label'),
            title: el.getAttribute('title'),
            role: el.getAttribute('role'),
            class: el.className,
            id: el.id
        });
    });

    return results;
    """

    try:
        elements = messenger.driver.execute_script(js_script)

        if elements:
            print(f"Found {len(elements)} potential attach button elements:\n")
            for i, el in enumerate(elements, 1):
                print(f"{i}. Element:")
                print(f"   Tag: {el.get('tag')}")
                print(f"   data-icon: {el.get('dataIcon')}")
                print(f"   aria-label: {el.get('ariaLabel')}")
                print(f"   title: {el.get('title')}")
                print(f"   role: {el.get('role')}")
                print(f"   class: {el.get('class')}")
                print(f"   id: {el.get('id')}")
                print()
        else:
            print("No potential attach buttons found with common patterns")
            print("\nLet me try broader search...")

            # Broader search
            broader_script = """
            let results = [];
            let buttons = document.querySelectorAll('button, [role="button"]');
            buttons.forEach(btn => {
                let text = btn.textContent.toLowerCase();
                let ariaLabel = (btn.getAttribute('aria-label') || '').toLowerCase();
                let title = (btn.getAttribute('title') || '').toLowerCase();

                if (text.includes('attach') || ariaLabel.includes('attach') || title.includes('attach') ||
                    text.includes('clip') || ariaLabel.includes('clip') || title.includes('clip')) {
                    results.push({
                        tag: btn.tagName,
                        text: btn.textContent.substring(0, 50),
                        ariaLabel: btn.getAttribute('aria-label'),
                        title: btn.getAttribute('title'),
                        class: btn.className
                    });
                }
            });
            return results;
            """

            broader_elements = messenger.driver.execute_script(broader_script)
            if broader_elements:
                print(f"Found {len(broader_elements)} buttons with attach/clip keywords:\n")
                for i, el in enumerate(broader_elements, 1):
                    print(f"{i}. Element:")
                    print(f"   Tag: {el.get('tag')}")
                    print(f"   Text: {el.get('text')}")
                    print(f"   aria-label: {el.get('ariaLabel')}")
                    print(f"   title: {el.get('title')}")
                    print(f"   class: {el.get('class')}")
                    print()

    except Exception as e:
        print(f"Error executing JavaScript: {e}")

    print("\n" + "="*60)
    print("Taking a page source snapshot for manual inspection...")
    print("="*60)

    # Save page source
    with open('/tmp/whatsapp_page_source.html', 'w', encoding='utf-8') as f:
        f.write(messenger.driver.page_source)
    print("✓ Saved page source to: /tmp/whatsapp_page_source.html")

    # Look for input elements
    print("\nSearching for file input elements...")
    file_inputs = messenger.driver.find_elements(By.XPATH, '//input[@type="file"]')
    print(f"Found {len(file_inputs)} file input elements")

    for i, inp in enumerate(file_inputs, 1):
        print(f"\n{i}. File Input:")
        print(f"   Accept: {inp.get_attribute('accept')}")
        print(f"   Name: {inp.get_attribute('name')}")
        print(f"   Class: {inp.get_attribute('class')}")
        print(f"   ID: {inp.get_attribute('id')}")
        print(f"   Displayed: {inp.is_displayed()}")

    input("\nPress Enter to close browser and exit...")
    messenger.quit()
    print("Done.")

if __name__ == "__main__":
    inspect_dom()
