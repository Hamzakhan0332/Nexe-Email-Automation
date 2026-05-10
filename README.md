# 💌 Nexe Email Automation

Welcome to **Nexe Email Automation**! This is a simple, clean, and beginner-friendly Python script designed to automatically send scheduled emails using your own Gmail account. 

Instead of relying on clunky third-party SMTP setups, this script connects directly to the official **Gmail API**. This means your emails are sent securely and reliably, right from your actual outbox.

## 🌟 How It Works

1. **The Schedule:** Inside the script, there is a simple list of emails. You just tell it what time to send (like `00:17` or `18:00`), who to send it to, and what to say.
2. **The Watcher:** When you run the script, it stays awake in the background, quietly watching the system clock. 
3. **The Delivery:** As soon as the clock hits your scheduled time, it automatically uses your Gmail credentials behind the scenes and fires off the email.
4. **The History Log:** Every single email attempt (whether it succeeded or failed due to a dropped internet connection) is automatically recorded in a handy `nexe_email_log.csv` file. You will always have a perfect history of what was sent and when.

## 🛠️ Getting Started

### 1. Install the Requirements
Before you can run the script, you need to install a few helpful libraries. Open your terminal or command prompt and run:
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib schedule
```

### 2. Get Your Gmail Credentials
To let the script talk to your Gmail, you need a permission file from Google:
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project and enable the **Gmail API**.
3. Go to the **Credentials** tab and create an **OAuth client ID** (choose "Desktop app").
4. **Download the JSON file**. You don't need to manually copy any confusing Client IDs or Secrets! Just download the file directly.
5. Rename that downloaded file to exactly `credentials.json` and put it in the exact same folder as the Python script.

*(Note: If your Google project is in "Testing" mode, make sure to add your own email address to the "Test users" list on the OAuth consent screen page, otherwise Google will block your login!)*

### 3. Customize Your Schedule
Open `nexe_email_automation.py` in your text editor. Right near the top, you'll see the `SCHEDULED_EMAILS` list. Feel free to change the times (using 24-hour format), the recipients, the subjects, and the message body to whatever you need.

## 🚀 Running the Script

Once your `credentials.json` is in place, open your terminal and start the automation by running:
```bash
python nexe_email_automation.py
```

**The First Time You Run It:**
A browser window will pop up asking you to log into your Google account. Just click accept to grant the permissions to send emails. The script will automatically create a `token.json` file to remember your login. You'll never have to do this browser login step again!

**Waiting for the Magic:**
Once it's running, you'll see a message that says `"Waiting for scheduled times..."`. The terminal will look like it's frozen or stuck, but don't worry—that just means it's working perfectly and patiently watching the clock! 

Just leave the terminal open in the background, and it will handle the rest. If you ever want to stop the automation to make changes, just click into the terminal and press `Ctrl + C`.

---
*Built for the Nexe Email Automation project.*
