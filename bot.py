import os
import discord
import asyncio
import requests
from discord.ext import commands, tasks

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

API_URL = "https://api.arkhamintelligence.com/transfer/inflows"

HEADERS = {
    "accept": "application/json"
}

@bot.event
async def on_ready():
    print(f"Bot 上線：{bot.user}")
    whale_alert.start()

@tasks.loop(seconds=60)
async def whale_alert():
    try:
        resp = requests.get(API_URL, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            print("API Error:", resp.status_code)
            return

        data = resp.json()

        if not data or "inflows" not in data:
            print("No inflow data")
            return

        for tx in data["inflows"]:
            amount = tx.get("amount_usd", 0)
            if amount >= 10_000_000:
                chain = tx.get("chain", "unknown")
                src = tx.get("from_address", "N/A")
                dst = tx.get("to_address", "N/A")

                channel = bot.get_channel(CHANNEL_ID)
                if channel:
                    await channel.send(
                        f"🚨 **Whale Transfer Alert!**\n"
                        f"💰 Amount: ${amount:,.0f}\n"
                        f"🔗 Chain: {chain}\n"
                        f"↙ From: `{src}`\n"
                        f"↗ To: `{dst}`"
                    )
                await asyncio.sleep(1)

    except Exception as e:
        print("Error:", e)

@bot.command()
async def ping(ctx):
    await ctx.send("Bot Online!")

bot.run(TOKEN)
