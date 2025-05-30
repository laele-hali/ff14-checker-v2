FFXIV World Status Discord Bot

A lightweight Discord bot that monitors the status of Final Fantasy XIV game worlds and data centers using the official Lodestone server status page. It automatically alerts you in a designated channel whenever a tracked world or data center changes status (e.g., Online → Maintenance).
✨ Features

    ✅ Automatic checks every minute
    📋 Track individual worlds or entire data centers
    🔔 Sends Discord alerts on status changes only
    💬 Simple Discord commands to interact with the bot
    🔧 Configurable list of tracked items (via commands or JSON)

📦 Requirements

    Python 3.7+
    A Discord bot with message send/read permissions
    requests, discord.py, and beautifulsoup4 Python packages

Install dependencies:

pip install -r requirements.txt

🚀 Setup
1. Clone and Configure

git clone git clone https://github.com/laele-hali/ff14-checker-v2.git
cd ff14-checker-v2

cd ffxiv-status-bot

Edit bot.py:

    Replace "YOUR_DISCORD_BOT_TOKEN" with your bot's token.
    Set your CHANNEL_NAME to the name of the text channel for alerts (e.g., ff14-monitor).

2. Create tracked_items.json

This file lists the worlds and/or DCs the bot should monitor automatically:

[
  "Halicarnassus",
  "Marilith",
  "Dynamis"
]

You can also manage this list via Discord commands (!check add, !check remove).
🔧 Discord Bot Setup

Use the following URL format to invite your bot to your Discord server:

https://discord.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&scope=bot&permissions=3072

Recommended permissions:

    Send Messages

    Read Message History

💬 Supported Commands

    !check list — 📋 Check the current status of tracked items in the JSON file

    !check all — 🌍 Check all known worlds from Lodestone

    !check <name> — 🔍 Check a specific world or data center

    !check add <name> — ➕ Add a world or DC to the tracked list

    !check remove <name> — 🗑️ Remove a world or DC from the tracked list

🖥️ Run as a Background Service (Linux)

Create a systemd service for autostart and reliability:

# /etc/systemd/system/ffxivbot.service
[Unit]
Description=FFXIV Discord Status Bot
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/bot.py
WorkingDirectory=/path/to
Restart=always
User=your_user
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target

Enable and start the service:

sudo systemctl daemon-reload
sudo systemctl enable ffxivbot
sudo systemctl start ffxivbot

Check status with:
sudo systemctl status ffxivbot


📄 License

MIT License
