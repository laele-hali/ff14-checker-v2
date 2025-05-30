import discord
import requests
from bs4 import BeautifulSoup
import asyncio
import json
import os

# === Settings ===
TOKEN = "YOUR_DISCORD_BOT_TOKEN"
CHANNEL_NAME = "ff14-monitor"
CHECK_INTERVAL = 300  # seconds

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

tracked_file = "tracked_items.json"
status_icons = {
    "Online": "🟢",
    "Maintenance": "🔧",
    "Congested": "⛔",
    "Full": "⛔",
}
last_known_status = {}
dc_world_map = {}

# ✅ Updated Lodestone URL for EU region
LODESTONE_URL = "https://eu.finalfantasyxiv.com/lodestone/worldstatus/"

def load_tracked_items():
    if not os.path.exists(tracked_file):
        with open(tracked_file, "w") as f:
            json.dump([], f)
    with open(tracked_file, "r") as f:
        return json.load(f)

def save_tracked_items(items):
    with open(tracked_file, "w") as f:
        json.dump(items, f, indent=2)

def fetch_world_data():
    """Scrapes Lodestone to build DC -> Worlds map"""
    try:
        response = requests.get(LODESTONE_URL, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        dc_worlds = {}
        for dc_section in soup.select(".world-dcgroup"):
            dc_name = dc_section.select_one("h2").text.strip()
            worlds = [a.text.strip() for a in dc_section.select("table tbody tr td a")]
            dc_worlds[dc_name] = worlds
        return dc_worlds
    except Exception as e:
        print(f"Error building DC map: {e}")
        return {}

def fetch_world_status(world_names):
    try:
        response = requests.get(LODESTONE_URL, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        status_map = {}

        for world in world_names:
            entry = soup.find("a", text=world)
            if not entry:
                status_map[world] = ("Not found", "❓")
                continue
            row = entry.find_parent("tr")
            cell = row.find("td", class_="world-status")
            status = cell.get_text(strip=True)
            icon = status_icons.get(status, "⚠️")
            status_map[world] = (status, icon)

        return status_map
    except Exception as e:
        return {"error": f"⚠️ Error fetching Lodestone: {e}"}

def resolve_tracked_items(tracked_items):
    """Expands DCs into worlds"""
    expanded = []
    for item in tracke
