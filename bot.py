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
            entry = soup.find("a", string=world)
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
    for item in tracked_items:
        if item in dc_world_map:
            expanded.extend(dc_world_map[item])
        else:
            expanded.append(item)
    return list(set(expanded))  # remove duplicates

def format_status(status_map):
    if "error" in status_map:
        return status_map["error"]
    return "\n".join(f"**{w}**: {i} {s}" for w, (s, i) in status_map.items())

async def status_monitor():
    await client.wait_until_ready()
    channel = discord.utils.get(client.get_all_channels(), name=CHANNEL_NAME)
    if not channel:
        print(f"❌ Channel '{CHANNEL_NAME}' not found!")
        return

    while not client.is_closed():
        tracked = load_tracked_items()
        expanded = resolve_tracked_items(tracked)
        result = fetch_world_status(expanded)
        if "error" not in result:
            for world, (status, icon) in result.items():
                if last_known_status.get(world) != status:
                    last_known_status[world] = status
                    await channel.send(f"🔔 **{world}** status changed: {icon} {status}")
        await asyncio.sleep(CHECK_INTERVAL)

@client.event
async def on_ready():
    global dc_world_map
    dc_world_map = fetch_world_data()
    print(f"Logged in as {client.user}")
    client.loop.create_task(status_monitor())

@client.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.strip()
    lower = content.lower()

    if lower == "!check list":
        items = load_tracked_items()
        await message.channel.send("📋 Tracked items:\n" + "\n".join(items) if items else "No items tracked.")

    elif lower.startswith("!check add "):
        item = content[11:].title()
        items = load_tracked_items()
        if item not in items:
            items.append(item)
            save_tracked_items(items)
            await message.channel.send(f"✅ Added `{item}` to tracked list.")
        else:
            await message.channel.send(f"`{item}` is already tracked.")

    elif lower.startswith("!check remove "):
        item = content[14:].title()
        items = load_tracked_items()
        if item in items:
            items.remove(item)
            save_tracked_items(items)
            await message.channel.send(f"🗑️ Removed `{item}` from tracked list.")
        else:
            await message.channel.send(f"`{item}` is not in the tracked list.")

    elif lower == "!check all":
        items = load_tracked_items()
        expanded = resolve_tracked_items(items)
        result = fetch_world_status(expanded)
        await message.channel.send(format_status(result))

    elif lower.startswith("!check "):
        item = content[7:].title()
        worlds = dc_world_map.get(item, [item])
        result = fetch_world_status(worlds)
        await message.channel.send(format_status(result))

# === Start the bot ===
client.run(TOKEN)
