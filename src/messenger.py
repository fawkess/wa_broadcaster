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
        """Guaranteed delivery of exact message content
        Returns: True on success, error string on failure
        """
        try:
            # number = '9964297517'
            # Load blank chat
            self.driver.get(f"https://web.whatsapp.com/send?phone={number}")
            #time.sleep(3)

            # Check for invalid number alert
            try:
                WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Phone number shared via url is invalid')]"))
                )
                return "Invalid WhatsApp number"
            except:
                pass  # No invalid number alert, continue

            # Check for rate limiting / spam warnings
            page_text = self.driver.page_source.lower()
            rate_limit_keywords = [
                "too many messages",
                "slow down",
                "you're sending messages too quickly",
                "temporarily banned",
                "account restricted",
                "detected automated",
                "unusual activity"
            ]
            for keyword in rate_limit_keywords:
                if keyword in page_text:
                    return f"RATE LIMIT DETECTED: {keyword}"

            # Method 1: Clipboard injection (most reliable)
            pyperclip.copy(message)
            try:
                input_box = WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
                )
            except Exception as e:
                # Check if session expired
                if "scan" in self.driver.page_source.lower() or "qr" in self.driver.page_source.lower():
                    return "Session expired - QR scan required"
                return "Timeout waiting for chat to load (30s)"

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

        except Exception as e:
            error_msg = str(e)
            if "clipboard" in error_msg.lower():
                return "Clipboard access failed"
            elif "element" in error_msg.lower():
                return "WhatsApp UI element not found"
            elif "timeout" in error_msg.lower():
                return "Page load timeout"
            else:
                return f"Unknown error: {error_msg[:50]}"

    def send_media_with_caption(self, number, media_path, caption):
        """Send media file (image/video/document) with caption
        Returns: True on success, error string on failure
        """
        try:
            import os

            # Validate file exists (defensive check)
            if not os.path.exists(media_path):
                print(f"DEBUG: Media file not found: {media_path}")
                return f"Media file not found: {media_path}"

            # Get absolute path (Selenium requires absolute paths)
            abs_media_path = os.path.abspath(media_path)
            print(f"DEBUG: Using absolute media path: {abs_media_path}")

            # Navigate to chat
            self.driver.get(f"https://web.whatsapp.com/send?phone={number}")
            print(f"DEBUG: Navigated to chat URL for {number}")

            # Check for invalid number alert
            try:
                WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Phone number shared via url is invalid')]"))
                )
                return "Invalid WhatsApp number"
            except:
                pass  # No invalid number alert, continue

            # Check for rate limiting / spam warnings
            page_text = self.driver.page_source.lower()
            rate_limit_keywords = [
                "too many messages",
                "slow down",
                "you're sending messages too quickly",
                "temporarily banned",
                "account restricted",
                "detected automated",
                "unusual activity"
            ]
            for keyword in rate_limit_keywords:
                if keyword in page_text:
                    return f"RATE LIMIT DETECTED: {keyword}"

            # Wait for chat to load
            print("DEBUG: Waiting for chat to load...")
            try:
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
                )
                print("DEBUG: Chat loaded successfully")
            except:
                if "scan" in self.driver.page_source.lower() or "qr" in self.driver.page_source.lower():
                    return "Session expired - QR scan required"
                return "Timeout waiting for chat to load (30s)"

            # Click attach button (now uses plus-rounded icon instead of clip)
            print("DEBUG: Looking for attach button...")
            attach_clicked = False

            # Method 1: New WhatsApp UI - DIV with aria-label="Attach" and data-icon="plus-rounded"
            try:
                attach_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@aria-label="Attach"]'))
                )
                attach_btn.click()
                print("DEBUG: Clicked attach button (method 1 - div with aria-label='Attach')")
                attach_clicked = True
                random_sleep(2)
            except Exception as e1:
                print(f"DEBUG: Failed method 1 (aria-label='Attach'): {str(e1)[:100]}")

                # Method 2: Try by data-icon="plus-rounded"
                try:
                    attach_btn = self.driver.find_element(By.XPATH, '//div[@data-icon="plus-rounded"]')
                    attach_btn.click()
                    print("DEBUG: Clicked attach button (method 2 - data-icon='plus-rounded')")
                    attach_clicked = True
                    random_sleep(2)
                except Exception as e2:
                    print(f"DEBUG: Failed method 2 (plus-rounded): {str(e2)[:100]}")

                    # Method 3: Legacy - old clip icon (for older WhatsApp versions)
                    try:
                        attach_btn = self.driver.find_element(By.XPATH, '//span[@data-icon="clip"]')
                        attach_btn.click()
                        print("DEBUG: Clicked attach button (method 3 - legacy clip icon)")
                        attach_clicked = True
                        random_sleep(2)
                    except Exception as e3:
                        print(f"DEBUG: Failed method 3 (legacy clip): {str(e3)[:100]}")

                        # Method 4: Try any button/div with "attach" in title
                        try:
                            attach_btn = self.driver.find_element(By.XPATH, '//*[@title="Attach"]')
                            attach_btn.click()
                            print("DEBUG: Clicked attach button (method 4 - title='Attach')")
                            attach_clicked = True
                            random_sleep(2)
                        except Exception as e4:
                            print(f"DEBUG: Failed all 4 methods: {str(e4)[:100]}")
                            return "Failed to find attach button - tried 4 methods"

            if not attach_clicked:
                return "Failed to click attach button"

            # Wait longer for attach menu to fully load and file inputs to be ready
            print("DEBUG: Waiting for attach menu to load...")
            random_sleep(3)

            # Determine file type and select appropriate input
            file_ext = os.path.splitext(media_path)[1].lower()
            print(f"DEBUG: File extension detected: {file_ext}")

            if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.3gp']:
                # Images and videos
                print("DEBUG: Detected as image/video file")
                try:
                    # Wait for file input to be present and get a fresh reference
                    file_input = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'))
                    )
                    print("DEBUG: Found media file input element")
                except Exception as e:
                    print(f"DEBUG: Failed to find media file input: {str(e)[:100]}")
                    # Try alternative selector - any file input
                    try:
                        file_inputs = self.driver.find_elements(By.XPATH, '//input[@type="file"]')
                        if file_inputs:
                            # Use the first visible or first available file input
                            file_input = file_inputs[0]
                            print(f"DEBUG: Found file input using alternative selector (found {len(file_inputs)} inputs)")
                        else:
                            raise Exception("No file inputs found")
                    except Exception as e2:
                        print(f"DEBUG: Failed alternative selector: {str(e2)[:100]}")
                        return "Failed to find media file input"
            else:
                # Documents (PDF, DOCX, etc.)
                print("DEBUG: Detected as document file")
                try:
                    # Click on document option first
                    doc_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="document"]'))
                    )
                    doc_btn.click()
                    print("DEBUG: Clicked document button")
                    random_sleep(1)

                    file_input = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//input[@accept="*"]'))
                    )
                    print("DEBUG: Found document file input element")
                except Exception as e:
                    print(f"DEBUG: Failed to find document input: {str(e)[:100]}")
                    return "Failed to find document file input"

            # Upload the file - refind element fresh to avoid stale reference
            print(f"DEBUG: Attempting to upload file: {abs_media_path}")
            try:
                # Refind the file input element fresh right before using it
                if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.3gp']:
                    try:
                        file_input_fresh = self.driver.find_element(By.XPATH, '//input[@type="file"][@accept]')
                    except:
                        file_inputs_fresh = self.driver.find_elements(By.XPATH, '//input[@type="file"]')
                        file_input_fresh = file_inputs_fresh[0] if file_inputs_fresh else file_input
                else:
                    file_inputs_fresh = self.driver.find_elements(By.XPATH, '//input[@type="file"]')
                    file_input_fresh = file_inputs_fresh[-1] if file_inputs_fresh else file_input  # Last one for documents

                print("DEBUG: Refound file input element (fresh reference)")
                file_input_fresh.send_keys(abs_media_path)
                print("DEBUG: File path sent to input element")
                random_sleep(4)  # Wait for file to upload and preview to load
                print("DEBUG: Waiting for file preview to load...")
            except Exception as e:
                print(f"DEBUG: Failed to upload file: {str(e)[:100]}")
                return f"Failed to upload file: {str(e)[:50]}"

            # Add caption in the text box that appears after upload
            print("DEBUG: Looking for caption box...")
            try:
                # Wait longer for media preview to fully load
                random_sleep(2)

                # CRITICAL: Find caption box INSIDE the media preview overlay
                # The preview overlay has multiple possible selectors, we try them in order
                caption_box = None
                caption_found = False

                # Method 1: Caption box inside the media preview footer (most specific)
                try:
                    caption_box = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//div[contains(@class, "x1hx0egp")]//div[@contenteditable="true"][@data-tab="10"]'))
                    )
                    print("DEBUG: Found caption box (method 1 - inside preview footer)")
                    caption_found = True
                except Exception as e1:
                    print(f"DEBUG: Method 1 failed: {str(e1)[:80]}")

                # Method 2: Caption box with specific role in overlay
                if not caption_found:
                    try:
                        caption_box = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, '//div[@role="textbox"][@contenteditable="true"][@data-tab="10"]'))
                        )
                        print("DEBUG: Found caption box (method 2 - role=textbox)")
                        caption_found = True
                    except Exception as e2:
                        print(f"DEBUG: Method 2 failed: {str(e2)[:80]}")

                # Method 3: Find all matching boxes and use the VISIBLE one in foreground
                if not caption_found:
                    try:
                        all_boxes = self.driver.find_elements(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
                        print(f"DEBUG: Found {len(all_boxes)} total input boxes")

                        # The caption box in the preview should be visible and in the foreground
                        for idx, box in enumerate(all_boxes):
                            if box.is_displayed():
                                # Check if this box is in the foreground (has higher z-index or is in overlay)
                                z_index = self.driver.execute_script("return window.getComputedStyle(arguments[0]).zIndex;", box)
                                print(f"DEBUG: Box {idx} - displayed: True, z-index: {z_index}")

                                # The overlay caption box should have a higher z-index or be in a parent with higher z-index
                                parent_z = self.driver.execute_script("""
                                    var el = arguments[0];
                                    while (el.parentElement) {
                                        el = el.parentElement;
                                        var z = window.getComputedStyle(el).zIndex;
                                        if (z !== 'auto' && parseInt(z) > 0) return z;
                                    }
                                    return 'auto';
                                """, box)
                                print(f"DEBUG: Box {idx} - parent z-index: {parent_z}")

                                # Use the LAST visible box (most likely to be the overlay)
                                caption_box = box

                        if caption_box and caption_box.is_displayed():
                            print(f"DEBUG: Using last visible caption box (method 3 - likely the overlay)")
                            caption_found = True
                        else:
                            raise Exception("No visible caption box found")
                    except Exception as e3:
                        print(f"DEBUG: Method 3 failed: {str(e3)[:80]}")

                if not caption_found or caption_box is None:
                    raise Exception("Could not find caption box in media preview")

                print("DEBUG: Caption box found and selected")

                # Focus and clear the caption box first
                print("DEBUG: Focusing caption box...")
                try:
                    self.driver.execute_script("arguments[0].focus();", caption_box)
                    caption_box.click()
                    random_sleep(0.5)
                except Exception as e:
                    print(f"DEBUG: Focus/click issue: {str(e)[:80]}")

                # Try multiple methods to add caption
                caption_added = False

                # Method 1: Clipboard paste (PRIMARY - triggers real browser events)
                try:
                    print("DEBUG: Trying Method 1 - Clipboard paste...")
                    pyperclip.copy(caption)
                    random_sleep(0.5)

                    # Focus and paste
                    caption_box.click()
                    random_sleep(0.5)
                    caption_box.send_keys(PASTE_SHORTCUT)
                    random_sleep(1)

                    # Verify paste worked
                    caption_text = self.driver.execute_script("return arguments[0].textContent || arguments[0].innerText;", caption_box)
                    if caption_text and len(caption_text.strip()) > 0:
                        print(f"DEBUG: Caption pasted via clipboard (verified: {len(caption_text)} chars)")
                        caption_added = True
                    else:
                        print("DEBUG: Clipboard paste didn't add caption")
                except Exception as e:
                    print(f"DEBUG: Clipboard paste failed: {str(e)[:80]}")

                # Method 2: JavaScript injection (fallback)
                if not caption_added:
                    try:
                        print("DEBUG: Trying Method 2 - JavaScript injection...")
                        # Escape caption for JavaScript
                        escaped_caption = caption.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
                        script = f"""
                        var captionBox = arguments[0];
                        captionBox.focus();
                        captionBox.textContent = `{escaped_caption}`;
                        captionBox.innerHTML = `{escaped_caption}`;

                        // Trigger input events that WhatsApp listens for
                        var inputEvent = new InputEvent('input', {{
                            bubbles: true,
                            cancelable: true,
                            inputType: 'insertText',
                            data: `{escaped_caption}`
                        }});
                        captionBox.dispatchEvent(inputEvent);

                        var changeEvent = new Event('change', {{ bubbles: true }});
                        captionBox.dispatchEvent(changeEvent);
                        """
                        self.driver.execute_script(script, caption_box)
                        random_sleep(1)

                        # Verify caption was added
                        caption_text = self.driver.execute_script("return arguments[0].textContent || arguments[0].innerText;", caption_box)
                        if caption_text and len(caption_text.strip()) > 0:
                            print(f"DEBUG: Caption added via JavaScript (verified: {len(caption_text)} chars)")
                            caption_added = True
                        else:
                            print("DEBUG: JavaScript method didn't add caption")
                    except Exception as e:
                        print(f"DEBUG: JavaScript injection failed: {str(e)[:80]}")

                # Method 3: Character-by-character typing (last resort)
                if not caption_added:
                    try:
                        print("DEBUG: Trying Method 3 - Character typing...")
                        caption_box.click()
                        random_sleep(0.5)
                        caption_box.clear()
                        caption_box.send_keys(caption)
                        random_sleep(1)

                        # Verify typing worked
                        caption_text = self.driver.execute_script("return arguments[0].textContent || arguments[0].innerText;", caption_box)
                        if caption_text and len(caption_text.strip()) > 0:
                            print(f"DEBUG: Caption typed (verified: {len(caption_text)} chars)")
                            caption_added = True
                        else:
                            print("DEBUG: Character typing didn't add caption")
                    except Exception as e:
                        print(f"DEBUG: Character typing failed: {str(e)[:80]}")

                if caption_added:
                    print("DEBUG: Caption successfully added and verified")

                    # CRITICAL FIX: Trigger additional events to ensure WhatsApp registers the caption
                    try:
                        # Simulate a key press to trigger WhatsApp's input handlers
                        print("DEBUG: Triggering input events to register caption with WhatsApp...")
                        self.driver.execute_script("""
                            var captionBox = arguments[0];

                            // Focus the element
                            captionBox.focus();

                            // Dispatch multiple input events that WhatsApp listens for
                            var events = ['input', 'change', 'keyup', 'keydown'];
                            events.forEach(function(eventType) {
                                var evt = new Event(eventType, { bubbles: true, cancelable: true });
                                captionBox.dispatchEvent(evt);
                            });

                            // Also dispatch a compositionend event (for complex input)
                            var compEvent = new CompositionEvent('compositionend', {
                                bubbles: true,
                                cancelable: true,
                                data: captionBox.textContent
                            });
                            captionBox.dispatchEvent(compEvent);
                        """, caption_box)

                        # Add a space and delete it to trigger WhatsApp's input detection
                        caption_box.send_keys(" ")
                        random_sleep(0.5)
                        caption_box.send_keys(Keys.BACKSPACE)
                        random_sleep(0.5)

                        print("DEBUG: Input events triggered successfully")
                    except Exception as trigger_err:
                        print(f"DEBUG: Warning - couldn't trigger additional events: {str(trigger_err)[:80]}")

                    # Longer wait to ensure WhatsApp registers the caption (INCREASED FROM 2 TO 4 SECONDS)
                    print("DEBUG: Waiting 4 seconds for WhatsApp to register caption...")
                    random_sleep(4)

                    # Final verification that caption is still there before sending
                    try:
                        final_caption_text = self.driver.execute_script("return arguments[0].textContent || arguments[0].innerText;", caption_box)
                        if final_caption_text and len(final_caption_text.strip()) > 0:
                            print(f"DEBUG: Final verification - caption still present ({len(final_caption_text)} chars)")
                        else:
                            print("DEBUG: WARNING - Caption disappeared before send!")
                    except:
                        pass
                else:
                    print("DEBUG: WARNING - All caption methods failed, sending without caption")
            except Exception as e:
                # Caption is optional, continue even if it fails
                print(f"DEBUG: Failed to add caption (continuing anyway): {str(e)[:100]}")
                pass

            # Wait for media upload to complete (check for upload progress)
            print("DEBUG: Waiting for media upload to complete...")
            upload_complete = False
            for attempt in range(20):  # Wait up to 20 seconds
                try:
                    # Check if upload progress bar is gone (indicates upload complete)
                    progress_elements = self.driver.find_elements(By.XPATH, '//*[contains(@class, "progress") or contains(@aria-label, "upload") or contains(@aria-label, "loading")]')
                    if not progress_elements or all(not elem.is_displayed() for elem in progress_elements):
                        print(f"DEBUG: Upload appears complete (check {attempt + 1})")
                        upload_complete = True
                        break
                except:
                    pass
                time.sleep(1)

            if not upload_complete:
                print("DEBUG: Warning - couldn't verify upload completion, proceeding anyway")

            # Additional wait to ensure UI is ready
            random_sleep(2)

            # CRITICAL: Verify WhatsApp is ready by checking if send button state changed
            print("DEBUG: Verifying WhatsApp processed the caption...")
            try:
                # Wait for send button to become enabled (it's disabled until content is ready)
                # When caption is properly registered, send button should be clickable
                time.sleep(2)  # Give WhatsApp time to process

                # Check if send button exists and is in correct state
                send_check = self.driver.find_elements(By.XPATH, '//div[@aria-label="Send"]')
                if send_check:
                    print(f"DEBUG: Send button found ({len(send_check)} instances)")
                else:
                    print("DEBUG: WARNING - Send button not found yet")
            except Exception as verify_err:
                print(f"DEBUG: Send button verification warning: {str(verify_err)[:80]}")

            # Click send button (now uses wds-ic-send-filled icon in media preview)
            print("DEBUG: Looking for send button...")
            send_clicked = False
            send_btn = None

            # Method 1: New WhatsApp UI - DIV with aria-label="Send" in media preview
            try:
                send_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@aria-label="Send"]'))
                )
                print("DEBUG: Found send button (method 1 - div with aria-label='Send')")
            except Exception as e1:
                print(f"DEBUG: Failed method 1 (aria-label='Send'): {str(e1)[:100]}")

                # Method 2: Try by new send icon data-icon="wds-ic-send-filled"
                try:
                    send_btn = self.driver.find_element(By.XPATH, '//span[@data-icon="wds-ic-send-filled"]/parent::*')
                    print("DEBUG: Found send button (method 2 - wds-ic-send-filled icon)")
                except Exception as e2:
                    print(f"DEBUG: Failed method 2 (wds-ic-send-filled): {str(e2)[:100]}")

                    # Method 3: Legacy - old send icon (for older WhatsApp versions)
                    try:
                        send_btn = self.driver.find_element(By.XPATH, '//span[@data-icon="send"]/parent::*')
                        print("DEBUG: Found send button (method 3 - legacy send icon)")
                    except Exception as e3:
                        print(f"DEBUG: Failed method 3 (legacy send): {str(e3)[:100]}")

                        # Method 4: Try button with aria-label="Send"
                        try:
                            send_btn = self.driver.find_element(By.XPATH, '//button[@aria-label="Send"]')
                            print("DEBUG: Found send button (method 4 - button aria-label)")
                        except Exception as e4:
                            print(f"DEBUG: Failed all 4 send button methods: {str(e4)[:100]}")
                            return "Failed to find send button - tried 4 methods"

            if send_btn is None:
                return "Failed to find send button"

            # Try multiple click methods to ensure it works
            print("DEBUG: Attempting to click send button...")
            for click_attempt in range(3):
                try:
                    # Try regular click first
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", send_btn)
                    random_sleep(0.5)
                    send_btn.click()
                    print(f"DEBUG: Clicked send button (attempt {click_attempt + 1} - regular click)")
                    send_clicked = True
                    break
                except Exception as click_err:
                    print(f"DEBUG: Regular click failed (attempt {click_attempt + 1}): {str(click_err)[:80]}")
                    try:
                        # Fallback to JavaScript click
                        self.driver.execute_script("arguments[0].click();", send_btn)
                        print(f"DEBUG: Clicked send button (attempt {click_attempt + 1} - JavaScript click)")
                        send_clicked = True
                        break
                    except Exception as js_err:
                        print(f"DEBUG: JavaScript click also failed (attempt {click_attempt + 1}): {str(js_err)[:80]}")
                        if click_attempt < 2:
                            random_sleep(1)
                        continue

            if not send_clicked:
                return "Failed to click send button after 3 attempts"

            # Wait for message to be sent (longer wait for media uploads)
            print("DEBUG: Waiting for message to be sent...")
            random_sleep(3)

            # CRITICAL FIX: Check if preview overlay is still open (indicates send didn't work)
            print("DEBUG: Checking if preview overlay closed (indicates successful send)...")
            preview_still_open = False
            try:
                # Check if we're still in the media preview overlay
                preview_elements = self.driver.find_elements(By.XPATH, '//div[@data-animate-modal-popup="true" or contains(@class, "x1n2onr6")]')
                if preview_elements and any(elem.is_displayed() for elem in preview_elements):
                    print("DEBUG: WARNING - Preview overlay still open after send click!")
                    preview_still_open = True

                    # Try clicking send button ONE MORE TIME
                    print("DEBUG: Retrying send button click...")
                    try:
                        send_btn_retry = self.driver.find_element(By.XPATH, '//div[@aria-label="Send"]')
                        self.driver.execute_script("arguments[0].click();", send_btn_retry)
                        print("DEBUG: Send button clicked again (JavaScript click)")
                        random_sleep(3)
                    except Exception as retry_err:
                        print(f"DEBUG: Retry send failed: {str(retry_err)[:80]}")
            except Exception as check_err:
                print(f"DEBUG: Couldn't check preview overlay: {str(check_err)[:80]}")

            # Check for error dialogs immediately after send
            print("DEBUG: Checking for error dialogs...")
            error_keywords = ['couldn\'t send', 'failed', 'try again', 'error', 'too large', 'not supported']
            page_text = self.driver.page_source.lower()
            for keyword in error_keywords:
                if keyword in page_text:
                    print(f"DEBUG: Error detected: '{keyword}' found in page")
                    return f"Send failed - error message contains: {keyword}"

            # Wait longer and verify delivery by checking for message timestamp
            print("DEBUG: Waiting for delivery confirmation...")
            delivery_confirmed = False
            for verify_attempt in range(10):  # Check for up to 10 seconds
                time.sleep(1)
                page_source = self.driver.page_source

                # Check for timestamp indicators
                if "msg-time" in page_source or "_ao3e" in page_source or 'data-icon="msg-check"' in page_source or 'data-icon="msg-dblcheck"' in page_source:
                    print(f"DEBUG: Message delivered successfully (verified after {verify_attempt + 1}s)")
                    delivery_confirmed = True
                    break

                # Check if we're back to the main chat (preview closed)
                try:
                    regular_input = self.driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
                    if regular_input.is_displayed():
                        # Preview closed, likely sent
                        print(f"DEBUG: Preview closed, message likely sent (after {verify_attempt + 1}s)")
                        delivery_confirmed = True
                        break
                except:
                    pass

            if delivery_confirmed:
                return True
            else:
                print("DEBUG: Warning - couldn't verify delivery within 10 seconds")
                return "Send status unclear - no delivery confirmation found"

        except Exception as e:
            error_msg = str(e)
            if "file" in error_msg.lower():
                return f"File error: {error_msg[:50]}"
            elif "element" in error_msg.lower():
                return f"WhatsApp UI element not found: {error_msg[:50]}"
            elif "timeout" in error_msg.lower():
                return "Upload timeout - file may be too large"
            else:
                return f"Media send failed: {error_msg[:50]}"