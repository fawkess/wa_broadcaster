# WhatsApp Broadcaster - Mac Setup Instructions

## Prerequisites

1. **Python 3.8 or higher**
   - macOS usually comes with Python pre-installed
   - Check version first (Step 1), install if needed from https://www.python.org/downloads/

2. **Google Chrome Browser**
   - Download from https://www.google.com/chrome/
   - Must be installed before running the application

3. **Excel file with contacts** (provided in `config/contacts.xlsx`)

## Step 1: Verify Python Installation

Open **Terminal** (Press `Cmd + Space`, type `Terminal`, press Enter):

```bash
python3 --version
```

Expected output: `Python 3.8.x` or higher

If Python is not installed or version is too old:
- Download from https://www.python.org/downloads/macos/
- Or install via Homebrew: `brew install python3`

## Step 2: Download/Extract Project

1. Download the project ZIP or clone from Git
2. Extract to a folder, e.g., `/Users/yourname/wa_broadcaster/`
3. Note your project path - you'll need it for Step 3

## Step 3: Install Dependencies

Open **Terminal** and navigate to project folder:

```bash
cd ~/wa_broadcaster
pip3 install -r requirements.txt
```

**Alternative** if above doesn't work:
```bash
python3 -m pip install -r requirements.txt
```

Or install packages manually:
```bash
pip3 install selenium webdriver-manager pandas pyperclip openpyxl
```

**Expected output**: You should see successful installation messages for all 5 packages.

## Step 4: Configure Your Setup

### A. Prepare Contacts (Required)

1. Open `config/contacts.xlsx` in Excel or Numbers
2. Fill in three columns:
   - **Name**: Contact's full name
   - **WhatsApp Number**: Phone with country code (e.g., `919876543210` for India)
   - **nick_name**: Nickname for personalization (optional)

**Example:**
| Name | WhatsApp Number | nick_name |
|------|----------------|-----------|
| John Smith | 14155551234 | John |
| Priya Sharma | 919876543210 | Priya |

3. Save and close the file

### B. Edit Message Template (Required)

1. Open `config/message.txt` in TextEdit or any text editor
2. Write your message. Supports:
   - Multiple lines
   - Emojis (copy-paste or use `Cmd + Ctrl + Space` for emoji picker)
   - Special characters
   - Personalization: Use `<nick_name>` placeholder

**Example message:**
```
Hi <nick_name>,

Hope you're doing well!

We're excited to invite you to our upcoming event...

Best regards
```

3. Save the file

### C. Exclude Numbers (Optional)

If you want to skip certain numbers:
1. Open `config/exclude.txt`
2. Add phone numbers (one per line, with country code)
3. Save the file

**Example:**
```
919876543210
14155551234
```

### D. Configure Media Sending (Optional - NEW Feature!)

The broadcaster now supports sending media files (images, videos, documents) with your message as the caption!

#### To Enable Media Mode:

1. **Add your media file** to the `config/media/` folder:
   ```bash
   # Copy your image/video to the media folder
   cp /path/to/your/promo.jpg ~/wa_broadcaster/config/media/
   ```

2. **Edit `config.json`** and enable media mode:
   ```json
   {
     "send_as_media": true,
     "media_file": "config/media/promo.jpg"
   }
   ```

3. **Your message becomes the caption** - The text from `message.txt` will be sent as the media caption

#### Supported Media Types:

| Type | Formats | Max Size | Notes |
|------|---------|----------|-------|
| Images | `.jpg`, `.jpeg`, `.png`, `.gif` | 64MB | Best quality |
| Videos | `.mp4`, `.mov`, `.3gp` | 16MB | Compressed by WhatsApp |
| Documents | `.pdf`, `.docx`, `.txt`, `.xlsx` | 64MB | Sent as document |

#### Text-Only Mode (Default):

To send text messages without media (original behavior):
```json
{
  "send_as_media": false,
  "media_file": "config/media/sample.jpg"
}
```

When `send_as_media` is `false`, media file is ignored and normal text messages are sent.

### E. Update Configuration (Optional)

Edit `config.json` if you want to customize:

```json
{
  "default_delay": 15,          // Seconds between each message
  "timeouts": {
    "100": 30,                  // Pause 30 min after 100 messages
    "300": 30                   // Pause 30 min after 300 messages
  },
  "chrome_user_data": "/tmp/WhatsAppSession/Session1",

  "send_as_media": false,       // Set to true to send media
  "media_file": "config/media/sample.jpg"  // Path to your media file
}
```

**Mac paths** use forward slashes `/` (not backslashes like Windows).

## Step 5: Run the Application

Open **Terminal** and run:

```bash
cd ~/wa_broadcaster/src
python3 wa_broadcaster.py --config ../config.json
```

**Tip**: You can drag the `src` folder into Terminal after typing `cd ` to auto-fill the path.

## Step 6: First-Time Setup

When you run for the first time:

1. **Chrome Opens Automatically**
   - WhatsApp Web loads
   - Don't close this window

2. **Scan QR Code**
   - Open WhatsApp on your phone
   - Go to Settings > Linked Devices > Link a Device
   - Scan the QR code shown in Chrome

3. **Wait for WhatsApp to Load**
   - The application detects when you're logged in

4. **Test Message Verification**
   - Console prompts: "Enter your phone number for test message"
   - Enter your number (with country code, e.g., `919876543210`)
   - You'll receive a test message
   - Check the message formatting on your phone

5. **Confirm to Continue**
   - Console asks: "Did you receive the test message correctly? (Yes/No)"
   - Type `Yes` and press Enter to start bulk sending
   - Type `No` to abort

## Step 7: Monitor Progress

The application will:
- Send messages one by one with delay
- Show progress in Terminal: `[INFO] Sent to John Smith (919876543210)`
- Pause automatically at configured intervals (e.g., after 100 messages)
- Resume automatically after timeout

**Do NOT close Chrome window while running!**

## Output Files

Check the `config/` folder after running:

| File | Description |
|------|-------------|
| `whatsapp.log` | Complete log with timestamps |
| `sent_numbers.log` | Successfully sent numbers (prevents duplicates) |
| `failed_numbers.log` | Failed numbers with error messages |

## Resume Capability

If the script stops or you close it:

1. Simply run the command again
2. The app automatically:
   - Skips numbers in `sent_numbers.log`
   - Skips numbers in `exclude.txt`
   - Continues from where it stopped

**No need to edit anything - just re-run!**

## Troubleshooting

### Issue: "python3: command not found"

**Solution:**
1. Install Python from python.org
2. Or use Homebrew: `brew install python3`
3. Check: `which python3`

### Issue: "Chrome driver not found"

**Solution:**
- Ensure Google Chrome is installed in `/Applications/`
- The script auto-downloads ChromeDriver on first run
- Check your firewall/security settings

### Issue: "ModuleNotFoundError: No module named 'selenium'"

**Solution:**
```bash
cd ~/wa_broadcaster
pip3 install -r requirements.txt
```

If permission denied:
```bash
pip3 install --user -r requirements.txt
```

### Issue: "FileNotFoundError: config.json not found"

**Solution:**
- Make sure you're running from the `src` folder
- Check the path in command: `python3 wa_broadcaster.py --config ../config.json`
- Verify `config.json` exists in project root
- Use `ls -la ../config.json` to confirm

### Issue: Messages not formatting correctly

**Solution:**
- The test message step helps verify formatting
- Use `Cmd + Ctrl + Space` for emoji picker
- Line breaks are preserved automatically
- Copy-paste emojis from web if needed

### Issue: Account blocked / Rate limited

**Solution:**
- Increase `default_delay` to 20-30 seconds in `config.json`
- Add more frequent timeouts: `"50": 15` (pause 15 min after 50 messages)
- **Important**: Don't send more than 200-300 messages per day initially
- WhatsApp may flag accounts sending too many messages

### Issue: "Permission denied" on Chrome profile

**Solution:**
- Close all Chrome windows before running
- Change `chrome_user_data` path in `config.json` to:
  ```
  "chrome_user_data": "/Users/yourname/Documents/WhatsAppSession"
  ```
- Check folder permissions: `ls -la /tmp/WhatsAppSession/`

### Issue: Mac security blocks ChromeDriver

**Solution:**
1. Go to **System Preferences** > **Security & Privacy**
2. Click "Allow" when prompted about ChromeDriver
3. Or manually: Go to Downloads folder, right-click ChromeDriver, click "Open"

### Issue: pyperclip clipboard error

**Solution:**
Mac requires additional clipboard access:
```bash
pip3 install pyobjc-framework-Cocoa
```

Or grant Terminal clipboard access:
1. **System Preferences** > **Security & Privacy** > **Privacy** tab
2. Select "Accessibility" or "Automation"
3. Check the box for Terminal

### Issue: "Media file not found" error

**Solution:**
1. Check the file path in `config.json` is correct
2. Verify file exists:
   ```bash
   ls -la config/media/
   ```
3. Make sure path uses forward slashes: `config/media/promo.jpg`
4. Check file permissions: `chmod 644 config/media/promo.jpg`

### Issue: "Unsupported media format" error

**Solution:**
1. Check the file extension is supported (see Step 4D for supported formats)
2. Convert your file:
   - For images: Use Preview to export as `.jpg` or `.png`
   - For videos: Convert to `.mp4` using QuickTime or online converter
3. Supported extensions: `.jpg`, `.jpeg`, `.png`, `.gif`, `.mp4`, `.mov`, `.pdf`, `.docx`

### Issue: "Media file too large" error

**Solution:**
1. Check file size:
   ```bash
   ls -lh config/media/your_file.jpg
   ```
2. WhatsApp limits:
   - Images/Documents: 64MB max
   - Videos: 16MB max (recommended)
3. Compress the file:
   - **Images**: Open in Preview > File > Export > Reduce quality to 70-80%
   - **Videos**: Use QuickTime Player > File > Export As > 720p

### Issue: Media uploads but caption is missing

**Solution:**
- This is non-critical - media still sends successfully
- WhatsApp Web UI may have changed
- The caption box might not be found, but media is delivered
- Check your phone to verify caption appears

### Issue: "Failed to find attach button" error

**Solution:**
1. Ensure Chrome is up to date:
   - Chrome > About Google Chrome > Update if available
2. WhatsApp Web UI may have changed - wait for update
3. Check internet connection is stable
4. Try restarting Chrome and running again
5. Temporary workaround: Switch to text-only mode (`send_as_media: false`)

## Important Notes

### Chrome Profile Path
- First run creates a persistent Chrome profile
- Default: `/tmp/WhatsAppSession/Session1`
- This keeps WhatsApp logged in between runs
- To force new QR scan: `rm -rf /tmp/WhatsAppSession/`

### Phone Number Format
- Always include country code
- No spaces, dashes, or special characters
- Examples:
  - India: `919876543210` (not `+91 98765 43210`)
  - USA: `14155551234` (not `+1-415-555-1234`)

### Rate Limiting Best Practices
1. Start with 50-100 messages per day
2. Use 15-20 second delays
3. Add frequent timeout breaks
4. Gradually increase volume over weeks
5. Don't use on new WhatsApp accounts

### Excel File Format
- Must be `.xlsx` format (not `.xls` or `.csv`)
- Column names are case-sensitive: `Name`, `WhatsApp Number`, `nick_name`
- Save and close Excel/Numbers before running the script

### Media Sending Best Practices
1. **Test first**: Always send a test message to your own number to verify media displays correctly
2. **File size**: Keep images under 5MB and videos under 10MB for faster uploads
3. **Format**: Use `.jpg` for images and `.mp4` for videos for best compatibility
4. **Single file**: All contacts receive the same media file with personalized captions
5. **Switching modes**: You can switch between text-only and media mode by changing `send_as_media` in config
6. **Caption length**: Keep captions under 1000 characters for best results

### Running in Background

To run the script in background and log output:

```bash
cd ~/wa_broadcaster/src
nohup python3 wa_broadcaster.py --config ../config.json > output.log 2>&1 &
```

Check progress:
```bash
tail -f output.log
```

Stop background process:
```bash
ps aux | grep wa_broadcaster
kill <process_id>
```

## Getting Help

If you encounter issues:
1. Check `config/whatsapp.log` for detailed error messages
2. Verify all prerequisites are installed
3. Try running with a small test batch (3-5 contacts) first
4. Check that Chrome and WhatsApp Web are working normally in your browser
5. Ensure Mac security settings allow Terminal and Chrome to run

## Safety & Compliance

- Only send messages to contacts who have consented
- Respect WhatsApp's Terms of Service
- Use reasonable delays to avoid account restrictions
- This tool is for legitimate bulk messaging, not spam
