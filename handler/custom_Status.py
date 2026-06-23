import time
import math
import psutil
import re
import random
from datetime import datetime
import pytz

CLOCK_EMOJIS = [
    "🕛", "🕐", "🕑", "🕒", "🕓", "🕔",
    "🕕", "🕖", "🕗", "🕘", "🕙", "🕚"
]

def get_wind_direction(degrees):
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    emojis = ["⬆️", "↗️", "➡️", "↘️", "⬇️", "↙️", "⬅️", "↖️"]
    idx = int((degrees + 22.5) / 45) % 8
    return directions[idx], emojis[idx]

def get_weather_desc(code):
    wmo_codes = {
        0: ("☀️", "Clear"),
        1: ("🌤️", "Mainly Clear"),
        2: ("⛅", "Partly Cloudy"),
        3: ("☁️", "Overcast"),
        45: ("🌫️", "Fog"),
        48: ("🌫️", "Depositing Rime Fog"),
        51: ("🌧️", "Light Drizzle"),
        53: ("🌧️", "Moderate Drizzle"),
        55: ("🌧️", "Dense Drizzle"),
        56: ("🌧️", "Light Freezing Drizzle"),
        57: ("🌧️", "Dense Freezing Drizzle"),
        61: ("🌧️", "Slight Rain"),
        63: ("🌧️", "Moderate Rain"),
        65: ("🌧️", "Heavy Rain"),
        66: ("🌧️", "Light Freezing Rain"),
        67: ("🌧️", "Heavy Freezing Rain"),
        71: ("❄️", "Slight Snow Fall"),
        73: ("❄️", "Moderate Snow Fall"),
        75: ("❄️", "Heavy Snow Fall"),
        77: ("❄️", "Snow Grains"),
        80: ("🌦️", "Slight Rain Showers"),
        81: ("🌦️", "Moderate Rain Showers"),
        82: ("🌦️", "Violent Rain Showers"),
        85: ("❄️", "Slight Snow Showers"),
        86: ("❄️", "Heavy Snow Showers"),
        95: ("⛈️", "Thunderstorm"),
        96: ("⛈️", "Thunderstorm with Slight Hail"),
        99: ("⛈️", "Thunderstorm with Heavy Hail"),
    }
    return wmo_codes.get(code, ("🌡️", "Unknown"))

async def get_stats(bot):
    now = time.time()
    if not hasattr(bot, '_last_stats_update'):
        bot._last_stats_update = 0
        bot.geo_city = "Unknown"
        bot.geo_region = "Unknown"
        bot.geo_country = "Unknown"
        bot.geo_temp_c = 0
        bot.geo_temp_apparent = 0.0
        bot.geo_pressure_mb = 1013
        bot.geo_humidity = 50
        bot.geo_cloud = 0
        bot.geo_wind_kph = 0.0
        bot.geo_wind_dir = 0
        bot.geo_weather_code = 0
        bot.geo_timezone = None

    if now - bot._last_stats_update < 600:
        return

    import aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            config_ip = getattr(bot, "config", {}).get("ip", "default")
            if not config_ip or str(config_ip).strip().lower() == "default":
                url = "http://ip-api.com/json/"
            else:
                url = f"http://ip-api.com/json/{str(config_ip).strip()}"

            async with session.get(url, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("status") == "fail" and url != "http://ip-api.com/json/":
                        async with session.get("http://ip-api.com/json/", timeout=5) as fallback_resp:
                            if fallback_resp.status == 200:
                                data = await fallback_resp.json()

                    if data.get("status") != "fail":
                        bot.geo_country = data.get("country", "Unknown")
                        bot.geo_region = data.get("regionName", "Unknown")
                        bot.geo_city = data.get("city", "Unknown")
                        bot.geo_timezone = data.get("timezone", None)
                        lat = data.get("lat", 0)
                        lon = data.get("lon", 0)
                        
                        async with session.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,apparent_temperature,relative_humidity_2m,surface_pressure,cloud_cover,wind_speed_10m,wind_direction_10m,weather_code", timeout=5) as resp2:
                            if resp2.status == 200:
                                data2 = await resp2.json()
                                current = data2.get("current", {})
                                bot.geo_temp_c = current.get("temperature_2m", 0)
                                bot.geo_temp_apparent = current.get("apparent_temperature", bot.geo_temp_c)
                                bot.geo_pressure_mb = current.get("surface_pressure", 1013)
                                bot.geo_humidity = current.get("relative_humidity_2m", 50)
                                bot.geo_cloud = current.get("cloud_cover", 0)
                                bot.geo_wind_kph = current.get("wind_speed_10m", 0.0)
                                bot.geo_wind_dir = current.get("wind_direction_10m", 0)
                                bot.geo_weather_code = current.get("weather_code", 0)
        bot._last_stats_update = now
    except Exception:
        pass

async def parse_status(bot, text):
    if not text:
        return text

    await get_stats(bot)
    
    # Determine the timezone strictly from the resolved IP's geolocation
    tz = None
    geo_tz = getattr(bot, 'geo_timezone', None)
    if geo_tz:
        try:
            tz = pytz.timezone(geo_tz)
        except Exception:
            pass

    if tz:
        now = datetime.now(tz)
    else:
        now = datetime.now()
        
    hour = now.hour

    if "{emoji:time}" in text:
        emoji_time = "☀️" if 6 <= hour < 18 else "🌙"
        text = text.replace("{emoji:time}", emoji_time)

    if "{emoji:clock}" in text:
        text = text.replace("{emoji:clock}", CLOCK_EMOJIS[hour % 12])

    if "{ping}" in text:
        if math.isnan(bot.latency) or bot.latency == float('inf'):
            latency_ms = 0
        else:
            latency_ms = int(bot.latency * 1000)
        text = text.replace("{ping}", str(latency_ms))

    if "{cpu:speed}" in text:
        freq = psutil.cpu_freq()
        speed = round(freq.current / 1000, 1) if freq else 0
        text = text.replace("{cpu:speed}", str(speed))

    if "{cpu:usage}" in text:
        text = text.replace("{cpu:usage}", str(int(psutil.cpu_percent(interval=0))))

    if "{ram:usage}" in text:
        text = text.replace("{ram:usage}", str(int(psutil.virtual_memory().percent)))

    if "{temp:c}" in text:
        text = text.replace("{temp:c}", str(int(getattr(bot, 'geo_temp_c', 0))))

    if "{temp:f}" in text:
        temp_c = getattr(bot, 'geo_temp_c', 0)
        temp_f = round(temp_c * 9 / 5 + 32, 1)
        text = text.replace("{temp:f}", str(temp_f))

    if "{temp:apparent}" in text:
        text = text.replace("{temp:apparent}", str(int(getattr(bot, 'geo_temp_apparent', getattr(bot, 'geo_temp_c', 0)))))

    if "{city}" in text:
        text = text.replace("{city}", getattr(bot, 'geo_city', 'Unknown'))

    if "{region}" in text:
        text = text.replace("{region}", getattr(bot, 'geo_region', 'Unknown'))

    if "{country}" in text:
        text = text.replace("{country}", getattr(bot, 'geo_country', 'Unknown'))

    if "{date}" in text:
        text = text.replace("{date}", str(now.day))

    if "{month}" in text:
        text = text.replace("{month}", str(now.month))

    if "{year}" in text:
        text = text.replace("{year}", str(now.year))

    if "{hour}" in text:
        text = text.replace("{hour}", f"{(now.hour % 12 or 12):02d}")

    if "{hour24}" in text:
        text = text.replace("{hour24}", f"{now.hour:02d}")

    if "{min}" in text:
        text = text.replace("{min}", f"{now.minute:02d}")

    if "{uptime:days}" in text or "{uptime:hours}" in text or "{uptime:minutes}" in text or "{uptime:seconds}" in text:
        uptime_seconds = int(time.time() - getattr(bot, "start_time", time.time()))
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60

        text = text.replace("{uptime:days}", str(days))
        text = text.replace("{uptime:hours}", str(hours))
        text = text.replace("{uptime:minutes}", str(minutes))
        text = text.replace("{uptime:seconds}", str(seconds))

    if "{pressure:mb}" in text:
        text = text.replace("{pressure:mb}", str(int(getattr(bot, 'geo_pressure_mb', 1013))))

    if "{humidity}" in text:
        text = text.replace("{humidity}", str(int(getattr(bot, 'geo_humidity', 50))))

    if "{cloud}" in text:
        text = text.replace("{cloud}", str(int(getattr(bot, 'geo_cloud', 0))))

    if "{wind:kph}" in text:
        text = text.replace("{wind:kph}", str(getattr(bot, 'geo_wind_kph', 0.0)))

    if "{wind:mph}" in text:
        wind_kph = getattr(bot, 'geo_wind_kph', 0.0)
        wind_mph = round(wind_kph * 0.621371, 1)
        text = text.replace("{wind:mph}", str(wind_mph))

    if "{wind:dir}" in text:
        wind_dir_text, _ = get_wind_direction(getattr(bot, 'geo_wind_dir', 0))
        text = text.replace("{wind:dir}", wind_dir_text)

    if "{wind:dir_emoji}" in text:
        _, wind_dir_emoji = get_wind_direction(getattr(bot, 'geo_wind_dir', 0))
        text = text.replace("{wind:dir_emoji}", wind_dir_emoji)

    if "{weather:emoji}" in text:
        w_emoji, _ = get_weather_desc(getattr(bot, 'geo_weather_code', 0))
        text = text.replace("{weather:emoji}", w_emoji)

    if "{weather:desc}" in text:
        _, w_desc = get_weather_desc(getattr(bot, 'geo_weather_code', 0))
        text = text.replace("{weather:desc}", w_desc)

    
    matches = re.findall(r"\{random\((.*?)\)\}", text)
    for match in matches:
        options = [o.strip() for o in match.split(",")]
        if options:
            chosen = random.choice(options)
            text = text.replace(f"{{random({match})}}", chosen, 1)

    return text
