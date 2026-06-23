import discord
from discord.ext import tasks
import random
import asyncio
import yaml
from logger.logging import print_log, Colors

with open('config.yml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

async def start_rpc(client):
    print_log("[</>] Starting Custom RPC Loop...\n", Colors.green_to_cyan, interval=0.03)
    
    @tasks.loop(seconds=config.get("rpc_config", {}).get("delay", 5))
    async def rpc_loop():
        try:
            rpc_data = config.get("rpc_config", {}).get("data", [])
            if not rpc_data:
                return
                
            rpc = random.choice(rpc_data)
            
            if rpc.get("type") == "Spotify":
                activity = discord.Activity(
                    type=discord.ActivityType.listening,
                    name=rpc.get("title", "Glitch Music"),
                    details=rpc.get("artist", ""),
                    state=rpc.get("album", ""),
                    large_image_url=rpc.get("large_img"),
                    small_image_url=rpc.get("small_img")
                )
            else:
                activity = discord.Streaming(
                    name=rpc.get("title", "Live"),
                    url=rpc.get("btn1_url", "https://youtube.com"),
                    details=rpc.get("line2", ""),
                    state=rpc.get("line3", ""),
                    large_image_url=rpc.get("large_img"),
                    small_image_url=rpc.get("small_img")
                )
            
            await client.change_presence(status=discord.Status.online, activity=activity)
            print_log(f"[RPC] Updated → {rpc.get('type')} | {rpc.get('title')[:30]}...\n", Colors.cyan_to_blue, interval=0.02)
            
        except Exception as e:
            print_log(f"[RPC] Error: {e}\n", Colors.red_to_yellow, interval=0.02)

    rpc_loop.start()
