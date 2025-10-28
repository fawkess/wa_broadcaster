# WhatsApp Broadcaster - Windows Setup Instructions

## Prerequisites

1. **Python 3.8 or higher**
   - Download from https://www.python.org/downloads/
   - **IMPORTANT**: During installation, check "Add Python to PATH"

2. **Google Chrome Browser**
   - Download from https://www.google.com/chrome/
   - Must be installed before running the application

3. **Excel file with contacts** (provided in `config/contacts.xlsx`)

## Step 1: Verify Python Installation

Open **Command Prompt** (Press `Win + R`, type `cmd`, press Enter):

```cmd
python --version
```

Expected output: `Python 3.8.x` or higher

If command not found:
- Reinstall Python and check "Add Python to PATH"
- Or use full path: `C:\Python3X\python.exe --version`

## Step 2: Download/Extract Project

1. Download the project ZIP or clone from Git
2. Extract to a folder, e.g., `C:\wa_broadcaster\`
3. Note your project path - you'll need it for Step 3

## Step 3: Install Dependencies

Open **Command Prompt** and navigate to project folder:

```cmd
cd C:\wa_broadcaster
pip install -r requirements.txt
```

**Alternative commands** if above doesn't work:
```cmd
python -m pip install -r requirements.txt
```

Or install packages manually:
```cmd
pip install selenium webdriver-manager pandas pyperclip openpyxl
```

**Expected output**: You should see successful installation messages for all 5 packages.

## Step 4: Configure Your Setup

### A. Prepare Contacts (Required)

1. Open `config\contacts.xlsx` in Excel
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

1. Open `config\message.txt` in Notepad or any text editor
2. Write your message. Supports:
   - Multiple lines
   - Emojis (copy-paste from web)
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
1. Open `config\exclude.txt`
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

1. **Add your media file** to the `config\media\` folder:
   - Copy your image/video to: `C:\wa_broadcaster\config\media\`
   - For example: `promo.jpg`, `flyer.png`, `video.mp4`, `brochure.pdf`

2. **Edit `config.json`** and enable media mode:
   ```json
   {
     "send_as_media": true,
     "media_file": "config/media/promo.jpg"
   }
   ```

   **Note**: Use forward slashes `/` even on Windows in JSON files!

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
  "chrome_user_data": "C:\\Users\\YourName\\AppData\\Local\\WhatsAppSession",

  "send_as_media": false,       // Set to true to send media
  "media_file": "config/media/sample.jpg"  // Use forward slashes even on Windows!
}
```

**Important for Windows**:
- Use double backslashes `\\` for `chrome_user_data` path
- Use forward slashes `/` for `media_file` path (works cross-platform)

## Step 5: Run the Application

### Method 1: Using Command Prompt (Recommended)

Open **Command Prompt**:

```cmd
cd C:\wa_broadcaster\src
python wa_broadcaster.py --config ..\config.json
```

### Method 2: Using Batch File (Easier)

1. Double-click `run.bat` in the project root folder
2. The application will start automatically

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
- Show progress in console: `[INFO] Sent to John Smith (919876543210)`
- Pause automatically at configured intervals (e.g., after 100 messages)
- Resume automatically after timeout

**Do NOT close Chrome window while running!**

## Output Files

Check the `config\` folder after running:

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

### Issue: "python is not recognized"

**Solution:**
1. Reinstall Python from python.org
2. Check "Add Python to PATH" during installation
3. Or use: `C:\Users\YourName\AppData\Local\Programs\Python\Python3X\python.exe`

### Issue: "Chrome driver not found"

**Solution:**
- Ensure Google Chrome is installed
- The script auto-downloads ChromeDriver on first run
- Check your antivirus isn't blocking the download

### Issue: "ModuleNotFoundError: No module named 'selenium'"

**Solution:**
```cmd
cd C:\wa_broadcaster
pip install -r requirements.txt
```

### Issue: "FileNotFoundError: config.json not found"

**Solution:**
- Make sure you're running from the `src` folder
- Check the path in command: `python wa_broadcaster.py --config ..\config.json`
- Verify `config.json` exists in project root

### Issue: Messages not formatting correctly

**Solution:**
- The test message step helps verify formatting
- If emojis don't work, copy-paste from web sources
- Line breaks are preserved automatically

### Issue: Account blocked / Rate limited

**Solution:**
- Increase `default_delay` to 20-30 seconds in `config.json`
- Add more frequent timeouts: `"50": 15` (pause 15 min after 50 messages)
- **Important**: Don't send more than 200-300 messages per day initially
- WhatsApp may flag accounts sending too many messages

### Issue: "Access Denied" errors on Chrome profile

**Solution:**
- Close all Chrome windows before running
- Change `chrome_user_data` path in `config.json` to:
  ```
  "chrome_user_data": "C:\\Users\\YourName\\Documents\\WhatsAppSession"
  ```
- Run Command Prompt as Administrator

### Issue: "Media file not found" error

**Solution:**
1. Check the file path in `config.json` is correct
2. Verify file exists in File Explorer:
   - Navigate to `C:\wa_broadcaster\config\media\`
   - Check if your file is there
3. Use forward slashes in JSON: `config/media/promo.jpg`
4. Check file isn't locked or in use by another program

### Issue: "Unsupported media format" error

**Solution:**
1. Check the file extension is supported (see Step 4D for supported formats)
2. Convert your file:
   - For images: Use Paint or online converter to save as `.jpg` or `.png`
   - For videos: Use VLC or online converter to convert to `.mp4`
3. Supported extensions: `.jpg`, `.jpeg`, `.png`, `.gif`, `.mp4`, `.mov`, `.pdf`, `.docx`

### Issue: "Media file too large" error

**Solution:**
1. Check file size in File Explorer:
   - Right-click file > Properties > Size
2. WhatsApp limits:
   - Images/Documents: 64MB max
   - Videos: 16MB max (recommended)
3. Compress the file:
   - **Images**: Use Paint > Resize image to smaller dimensions
   - **Videos**: Use free tools like HandBrake to compress
   - Or use online compressors (search "compress image/video online")

### Issue: Media uploads but caption is missing

**Solution:**
- This is non-critical - media still sends successfully
- WhatsApp Web UI may have changed
- The caption box might not be found, but media is delivered
- Check your phone to verify caption appears

### Issue: "Failed to find attach button" error

**Solution:**
1. Ensure Chrome is up to date:
   - Chrome > Help > About Google Chrome > Update if available
2. WhatsApp Web UI may have changed - wait for update
3. Check internet connection is stable
4. Try restarting Chrome and running again
5. Temporary workaround: Switch to text-only mode (`send_as_media: false`)

## Important Notes

### Chrome Profile Path
- First run creates a persistent Chrome profile
- Default: `C:\Users\YourName\AppData\Local\Temp\WhatsAppSession\Session1`
- This keeps WhatsApp logged in between runs
- To force new QR scan: Delete this folder

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
- Save and close Excel before running the script

### Media Sending Best Practices
1. **Test first**: Always send a test message to your own number to verify media displays correctly
2. **File size**: Keep images under 5MB and videos under 10MB for faster uploads
3. **Format**: Use `.jpg` for images and `.mp4` for videos for best compatibility
4. **Single file**: All contacts receive the same media file with personalized captions
5. **Switching modes**: You can switch between text-only and media mode by changing `send_as_media` in config
6. **Caption length**: Keep captions under 1000 characters for best results

## Getting Help

If you encounter issues:
1. Check `config\whatsapp.log` for detailed error messages
2. Verify all prerequisites are installed
3. Try running with a small test batch (3-5 contacts) first
4. Check that Chrome and WhatsApp Web are working normally in your browser

## Safety & Compliance

- Only send messages to contacts who have consented
- Respect WhatsApp's Terms of Service
- Use reasonable delays to avoid account restrictions
- This tool is for legitimate bulk messaging, not spam
