#!/usr/bin/env python3
"""
Automatic DOM Inspector - Find current WhatsApp Web selectors without interaction
"""
import sys
import time
from messenger import WhatsAppMessenger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def auto_inspect():
    print("=== Automatic WhatsApp Web DOM Inspector ===\n")

    if len(sys.argv) < 2:
        print("Usage: python3 auto_inspect_dom.py <phone_number>")
        sys.exit(1)

    test_number = sys.argv[1]
    chrome_user_data = "/tmp/WhatsAppSession/Session1"

    print(f"Phone Number: {test_number}")
    print(f"Chrome Profile: {chrome_user_data}\n")

    # Initialize messenger
    messenger = WhatsAppMessenger(chrome_user_data)

    # Login
    print("Opening WhatsApp Web...")
    messenger.login()

    # Navigate to chat
    print(f"Navigating to chat with {test_number}...")
    messenger.driver.get(f"https://web.whatsapp.com/send?phone={test_number}")

    # Wait for chat to load
    print("Waiting for chat to load...")
    try:
        WebDriverWait(messenger.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
        )
        print("✓ Chat loaded\n")
    except:
        print("⚠️  Timeout waiting for chat\n")

    time.sleep(3)  # Extra wait for full render

    print("="*60)
    print("INSPECTING DOM FOR ATTACH BUTTON...")
    print("="*60 + "\n")

    # JavaScript to find all possible attach button elements
    js_script = """
    let results = {
        clipIcons: [],
        plusIcons: [],
        attachButtons: [],
        allButtons: [],
        fileInputs: []
    };

    // 1. Find elements with 'clip' in data-icon
    document.querySelectorAll('[data-icon]').forEach(el => {
        let icon = el.getAttribute('data-icon');
        if (icon && icon.toLowerCase().includes('clip')) {
            results.clipIcons.push({
                tag: el.tagName,
                dataIcon: icon,
                ariaLabel: el.getAttribute('aria-label'),
                title: el.getAttribute('title'),
                role: el.getAttribute('role'),
                class: el.className,
                xpath: getXPath(el)
            });
        }
        if (icon && icon.toLowerCase().includes('plus')) {
            results.plusIcons.push({
                tag: el.tagName,
                dataIcon: icon,
                ariaLabel: el.getAttribute('aria-label'),
                title: el.getAttribute('title'),
                role: el.getAttribute('role'),
                class: el.className,
                xpath: getXPath(el)
            });
        }
    });

    // 2. Find buttons with attach-related text
    document.querySelectorAll('button, [role="button"], div[role="button"]').forEach(btn => {
        let ariaLabel = (btn.getAttribute('aria-label') || '').toLowerCase();
        let title = (btn.getAttribute('title') || '').toLowerCase();

        if (ariaLabel.includes('attach') || title.includes('attach') ||
            ariaLabel.includes('clip') || title.includes('clip')) {
            results.attachButtons.push({
                tag: btn.tagName,
                ariaLabel: btn.getAttribute('aria-label'),
                title: btn.getAttribute('title'),
                class: btn.className,
                xpath: getXPath(btn)
            });
        }
    });

    // 3. Get all buttons in the footer area (where attach usually is)
    let footer = document.querySelector('footer');
    if (footer) {
        footer.querySelectorAll('button, [role="button"], div[role="button"]').forEach(btn => {
            results.allButtons.push({
                tag: btn.tagName,
                ariaLabel: btn.getAttribute('aria-label'),
                title: btn.getAttribute('title'),
                dataIcon: btn.querySelector('[data-icon]')?.getAttribute('data-icon'),
                class: btn.className,
                xpath: getXPath(btn)
            });
        });
    }

    // 4. Find all file inputs
    document.querySelectorAll('input[type="file"]').forEach(inp => {
        results.fileInputs.push({
            accept: inp.getAttribute('accept'),
            name: inp.getAttribute('name'),
            class: inp.className,
            id: inp.id,
            displayed: inp.offsetParent !== null
        });
    });

    function getXPath(element) {
        if (element.id !== '')
            return 'id("' + element.id + '")';
        if (element === document.body)
            return element.tagName;
        let ix = 0;
        let siblings = element.parentNode.childNodes;
        for (let i = 0; i < siblings.length; i++) {
            let sibling = siblings[i];
            if (sibling === element)
                return getXPath(element.parentNode) + '/' + element.tagName + '[' + (ix + 1) + ']';
            if (sibling.nodeType === 1 && sibling.tagName === element.tagName)
                ix++;
        }
    }

    return results;
    """

    try:
        results = messenger.driver.execute_script(js_script)

        print("1. CLIP ICONS:")
        if results['clipIcons']:
            for i, el in enumerate(results['clipIcons'], 1):
                print(f"   [{i}] data-icon='{el['dataIcon']}' | aria-label='{el['ariaLabel']}' | title='{el['title']}'")
        else:
            print("   None found")

        print("\n2. PLUS ICONS:")
        if results['plusIcons']:
            for i, el in enumerate(results['plusIcons'], 1):
                print(f"   [{i}] data-icon='{el['dataIcon']}' | aria-label='{el['ariaLabel']}' | title='{el['title']}'")
        else:
            print("   None found")

        print("\n3. BUTTONS WITH ATTACH/CLIP TEXT:")
        if results['attachButtons']:
            for i, el in enumerate(results['attachButtons'], 1):
                print(f"   [{i}] {el['tag']} | aria-label='{el['ariaLabel']}' | title='{el['title']}'")
        else:
            print("   None found")

        print("\n4. ALL FOOTER BUTTONS:")
        if results['allButtons']:
            print(f"   Found {len(results['allButtons'])} buttons in footer:")
            for i, el in enumerate(results['allButtons'], 1):
                print(f"   [{i}] {el['tag']} | data-icon='{el['dataIcon']}' | aria-label='{el['ariaLabel']}' | title='{el['title']}'")
        else:
            print("   No footer found or no buttons in footer")

        print("\n5. FILE INPUT ELEMENTS:")
        if results['fileInputs']:
            print(f"   Found {len(results['fileInputs'])} file inputs:")
            for i, inp in enumerate(results['fileInputs'], 1):
                print(f"   [{i}] accept='{inp['accept']}' | displayed={inp['displayed']}")
        else:
            print("   None found")

    except Exception as e:
        print(f"Error executing JavaScript: {e}")

    # Save page source for manual inspection
    print("\n" + "="*60)
    print("SAVING PAGE SOURCE...")
    print("="*60)
    with open('/tmp/whatsapp_dom.html', 'w', encoding='utf-8') as f:
        f.write(messenger.driver.page_source)
    print("✓ Saved to: /tmp/whatsapp_dom.html")
    print("  You can search this file for 'attach', 'clip', 'plus' keywords")

    print("\nClosing browser...")
    messenger.quit()
    print("Done.")

if __name__ == "__main__":
    auto_inspect()
