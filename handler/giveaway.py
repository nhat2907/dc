import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import discord
from logger.logging import print_log, Colors
from logger.connector import log_giveaway

async def process_giveaway(bot, message):
    giveaway_cfg = bot.config.get("giveaway_joiner", {})
    if not giveaway_cfg.get("enabled", False):
        return

    if not message.author or message.author.id not in [530082442967646230, 294882584201003009, 235148962103951360, 1103932552701550622]:
        return

    if not message.components:
        return

    if message.id in bot.joined_giveaways:
        return

    for row in message.components:
        for component in row.children:
            is_button = False
            if hasattr(component, 'type') and str(component.type) in ['ComponentType.button', 'button', '1', 1]:
                is_button = True
            elif type(component).__name__ == 'Button':
                is_button = True
            elif hasattr(component, 'click'):
                is_button = True

            if not is_button:
                continue

            has_firework = False
            if component.emoji:
                if str(component.emoji) == "🎉" or getattr(component.emoji, 'name', '') == "🎉":
                    has_firework = True
            if component.label and "🎉" in component.label:
                has_firework = True

            if has_firework and not component.disabled:
                bot.joined_giveaways.add(message.id)
                success = False
                try:
                    await component.click()
                    success = True
                except Exception as e:
                    err_msg = str(e).lower()
                    is_timeout = "timeout" in err_msg or "did not receive a response" in err_msg or isinstance(e, asyncio.TimeoutError)
                    if is_timeout:
                        success = True
                    else:
                        bot.joined_giveaways.discard(message.id)
                        if giveaway_cfg.get("logging", True):
                            print_log(f"[!] Error clicking button: {e}\n", Colors.red_to_yellow, interval=0)
                
                if success:
                    if giveaway_cfg.get("logging", True):
                        server_id = message.guild.id if message.guild else "DM"
                        print_log(f"[</>] Joined Giveaway | {server_id}\n", Colors.green_to_cyan, interval=0)
                    
                    webhook_cfg = bot.config.get("webhook_logging", {})
                    if webhook_cfg.get("enabled", False) and webhook_cfg.get("webhook_url"):
                        g_name = message.guild.name if message.guild else "DM"
                        g_id = message.guild.id if message.guild else "N/A"
                        c_name = message.channel.name if hasattr(message.channel, "name") else str(message.channel)
                        c_id = message.channel.id
                        asyncio.create_task(log_giveaway(webhook_cfg["webhook_url"], g_name, g_id, c_name, c_id))
                    return

if __name__ == "__main__":
    print("[</>] This is a modular handler and should be run via bot.py, not directly.")
