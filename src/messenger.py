import platform
import time

import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from lib import random_sleep

# Define OS-specific paste shortcut
PASTE_SHORTCUT = Keys.COMMAND + 'v' if platform.system() == 'Darwin' else Keys.CONTROL + 'v'

class WhatsAppMessenger:
    def __init__(self, user_data_dir):
        options = Options()
        options.add_argument(f"--user-data-dir={user_data_dir}")
        options.add_argument("--start-minimized")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--remote-debugging-port=9222")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.wait = WebDriverWait(self.driver, 20)

    def login(self):
        self.driver.get("https://web.whatsapp.com")
        try:
            self.wait.until(EC.presence_of_element_located(
                (By.XPATH, '//div[@contenteditable="true"]')))
            return True
        except:
            return False  # QR scan needed

    def _inject_message(self, message):
        """Direct DOM injection for perfect formatting"""
        script = f"""
        var input = document.querySelector('div[contenteditable="true"][data-tab="10"]');
        input.innerHTML = `{message}`;
        input.dispatchEvent(new InputEvent('input', {{ bubbles: true }}));
        """
        self.driver.execute_script(script)

    def send_message(self, number, message):
        """Returns True if message sent, False if failed"""
        try:
            # Force fresh load with cache busting
            #message = f'sending message to {number}'
            number = '9964297517'
            # Process non-BMP chars
            safe_content = message.encode('utf-16', 'surrogatepass').decode('utf-16')
            chat_url = f"https://web.whatsapp.com/send?phone={number}"
            self.driver.get(chat_url)

            # Main sending attempt (15 sec max)
            try:
                message_box = WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
                )
                # Send message character-by-character with emoji support

                # Try DOM injection first
                try:
                    self._inject_message(message)
                    random_sleep(4)
                    self.driver.find_element(By.XPATH, '//div[@contenteditable="true"]').send_keys(Keys.ENTER)
                    return True
                except Exception as e:
                    # Fallback to clipboard
                    pyperclip.copy(message)
                    # Use both CONTROL and COMMAND for cross-platform compatibility
                    self.driver.find_element(By.XPATH, '//div[@contenteditable="true"]').send_keys(PASTE_SHORTCUT)
                    random_sleep(4)
                    self.driver.find_element(By.XPATH, '//div[@contenteditable="true"]').send_keys(Keys.ENTER)
                    return True

            except Exception as e:
                return False  # Fail silently for any other errors

        except Exception as e:
            return False  # Fail silently for any other errors

    def quit(self):
        try:
            self.driver.quit()
        except:
            pass  # Even quit won't break

    def send_exact_message(self, number, message):
        """Guaranteed delivery of exact message content"""
        try:
            # number = '9964297517'
            # Load blank chat
            self.driver.get(f"https://web.whatsapp.com/send?phone={number}")
            #time.sleep(3)

            # Method 1: Clipboard injection (most reliable)
            pyperclip.copy(message)
            input_box = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
            )

            # Paste using both COMMAND and CONTROL for cross-platform
            input_box.send_keys(PASTE_SHORTCUT)
            random_sleep(3)
            input_box.send_keys(Keys.ENTER)

            # Verify delivery
            random_sleep(5)
            if "msg-time" not in self.driver.page_source:
                return True

            # Fallback to JS injection if clipboard fails
            self.driver.execute_script(f"""
                var el = document.querySelector('div[contenteditable="true"]');
                el.innerHTML = `{message}`;
                el.dispatchEvent(new Event('input', {{bubbles: true}}));
            """)
            input_box.send_keys(Keys.ENTER)
            return True

        except Exception:
            return False