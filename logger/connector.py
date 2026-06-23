import aiohttp
from datetime import datetime, timezone

async def send_webhook(webhook_url, payload):
    if not webhook_url:
        return
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as resp:
                await resp.read()
    except Exception:
        pass

async def log_giveaway(webhook_url, guild_name, guild_id, channel_name, channel_id):
    now_iso = datetime.now(timezone.utc).isoformat()
    payload = {
        "embeds": [
            {
                "author": {
                    "name": "Joined Giveaway Successfully",
                    "icon_url": "https://cdn3.emoji.gg/emojis/138056-check.gif"
                },
                "color": 3066993,
                "fields": [
                    {"name": "Guild Name", "value": str(guild_name), "inline": True},
                    {"name": "Guild ID", "value": str(guild_id), "inline": True},
                    {"name": "Channel Name", "value": str(channel_name), "inline": True},
                    {"name": "Channel ID", "value": str(channel_id), "inline": True},
                    {"name": "Joined At", "value": f"<t:{int(datetime.now().timestamp())}:F>", "inline": False}
                ],
                "image": {
                    "url": "https://cdn2.unrealengine.com/what-is-discord-1920x1080-c3d90ca45f57.jpg"
                },
                "footer": {
                    "text": "made w love",
                },
            }
        ]
    }
    await send_webhook(webhook_url, payload)

async def log_quest(webhook_url, quest_name, quest_type, orbs_received):
    now_iso = datetime.now(timezone.utc).isoformat()
    payload = {
        "embeds": [
            {
                "author": {
                    "name": "Quest Completed",
                    "icon_url": "https://cdn3.emoji.gg/emojis/138056-check.gif"
                },
                "color": 3066993,
                "fields": [
                    {"name": "Quest Name", "value": str(quest_name), "inline": True},
                    {"name": "Quest Type", "value": str(quest_type), "inline": True},
                    {"name": "Orbs Received", "value": str(orbs_received), "inline": True}
                ],
                "image": {
                    "url": "https://cdn2.unrealengine.com/what-is-discord-1920x1080-c3d90ca45f57.jpg"
                },
                "footer": {
                    "text": "made w love",
                },
            }
        ]
    }
    await send_webhook(webhook_url, payload)
