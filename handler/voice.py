import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json

async def connect_voice(bot):
    voice_cfg = bot.config.get("voice_config", {})
    if not voice_cfg.get("enabled", False):
        return

    guild_id = voice_cfg.get("guild_id")
    channel_id = voice_cfg.get("channel_id")
    if not guild_id or not channel_id:
        return

    try:
        payload = {
            "op": 4,
            "d": {
                "guild_id": str(guild_id),
                "channel_id": str(channel_id),
                "self_mute": True,
                "self_deaf": True,
                "self_stream": False,
                "self_video": False
            }
        }
        if hasattr(bot.ws, 'send_as_json'):
            await bot.ws.send_as_json(payload)
        else:
            await bot.ws.send(json.dumps(payload))
    except Exception:
        pass

async def handle_voice_state_update(bot, before, after):
    voice_cfg = bot.config.get("voice_config", {})
    if not voice_cfg.get("enabled", False):
        return

    guild_id = voice_cfg.get("guild_id")
    channel_id = voice_cfg.get("channel_id")
    if not guild_id or not channel_id:
        return

    if after.channel and str(after.channel.id) == str(channel_id):
        if getattr(bot, 'voice_live_started', False):
            return
        bot.voice_live_started = True

        try:
            payload = {
                "op": 4,
                "d": {
                    "guild_id": str(guild_id),
                    "channel_id": str(channel_id),
                    "self_mute": True,
                    "self_deaf": True,
                    "self_stream": True,
                    "self_video": False
                }
            }
            if hasattr(bot.ws, 'send_as_json'):
                await bot.ws.send_as_json(payload)
            else:
                await bot.ws.send(json.dumps(payload))

            stream_payload = {
                "op": 18,
                "d": {
                    "type": "guild",
                    "guild_id": str(guild_id),
                    "channel_id": str(channel_id),
                    "preferred_region": "singapore"
                }
            }
            if hasattr(bot.ws, 'send_as_json'):
                await bot.ws.send_as_json(stream_payload)
            else:
                await bot.ws.send(json.dumps(stream_payload))

            await asyncio.sleep(0.5)

            video_payload = {
                "op": 4,
                "d": {
                    "guild_id": str(guild_id),
                    "channel_id": str(channel_id),
                    "self_mute": True,
                    "self_deaf": True,
                    "self_stream": True,
                    "self_video": True
                }
            }
            if hasattr(bot.ws, 'send_as_json'):
                await bot.ws.send_as_json(video_payload)
            else:
                await bot.ws.send(json.dumps(video_payload))
        except Exception:
            bot.voice_live_started = False
            pass
    elif not after.channel:
        bot.voice_live_started = False

if __name__ == "__main__":
    print("[</>] This is a modular handler and should be run via bot.py, not directly.")
