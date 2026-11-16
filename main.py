
import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from datetime import datetime

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "world_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {
        "news": [],
        "bounties": {},
        "yonkou": [],
        "marine": {},
        "government": [],
        "companies": [],
        "islands": [],
        "events": [],
        "archive": []
    }

data = load_data()

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def make_embed(title, description):
    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.gold(),
        timestamp=datetime.now()
    )
    embed.set_footer(text="『📰』WORLD ECONOMY")
    return embed

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"WORLD ECONOMY online as {bot.user}")

@bot.tree.command(name="news", description="Publish a world news report")
@app_commands.describe(title="News headline", message="News content")
async def news(interaction: discord.Interaction, title: str, message: str):
    data["news"].append({
        "title": title,
        "message": message,
        "author": str(interaction.user),
        "date": datetime.now().isoformat()
    })
    save_data()

    await interaction.response.send_message(
        embed=make_embed(f"📰 {title}", message)
    )

@bot.tree.command(name="newspaper", description="Create a newspaper edition")
async def newspaper(interaction: discord.Interaction):
    latest = data["news"][-5:]
    description = "\n\n".join(
        f"**{item['title']}**\n{item['message']}"
        for item in reversed(latest)
    )
    if not description:
        description = "No news published yet."

    await interaction.response.send_message(
        embed=make_embed("🌍 WORLD ECONOMY – DAILY EDITION", description)
    )

@bot.tree.command(name="bounty", description="Register a wanted bounty")
@app_commands.describe(player="Pirate name", amount="Bounty in Berries")
async def bounty(interaction: discord.Interaction, player: str, amount: int):
    if amount < 0:
        await interaction.response.send_message(
            "Bounty cannot be negative.", ephemeral=True
        )
        return

    data["bounties"][player] = amount
    save_data()

    embed = make_embed(
        "💰 WANTED – DEAD OR ALIVE",
        f"**{player}**\nBounty: ฿{amount:,}"
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="yonkou", description="Manage the Four Emperors")
@app_commands.describe(action="add or remove", name="Pirate name")
async def yonkou(interaction: discord.Interaction, action: str, name: str):
    if action.lower() == "add":
        if name not in data["yonkou"]:
            data["yonkou"].append(name)
    elif action.lower() == "remove":
        if name in data["yonkou"]:
            data["yonkou"].remove(name)
    else:
        await interaction.response.send_message(
            "Use add or remove.", ephemeral=True
        )
        return

    save_data()
    await interaction.response.send_message(
        embed=make_embed("👑 YONKOU", "\n".join(data["yonkou"]) or "No Yonkou registered.")
    )

@bot.tree.command(name="marine", description="Register a Marine officer")
@app_commands.describe(name="Officer name", rank="Marine rank")
async def marine(interaction: discord.Interaction, name: str, rank: str):
    data["marine"][name] = rank
    save_data()
    await interaction.response.send_message(
        embed=make_embed("⚓ MARINE DATABASE", f"**{name}**\nRank: {rank}")
    )

@bot.tree.command(name="government", description="Register a government member")
@app_commands.describe(name="Member name", position="Government position")
async def government(interaction: discord.Interaction, name: str, position: str):
    data["government"].append({
        "name": name,
        "position": position
    })
    save_data()
    await interaction.response.send_message(
        embed=make_embed("👑 WORLD GOVERNMENT", f"**{name}**\nPosition: {position}")
    )

@bot.tree.command(name="company", description="Register a company")
@app_commands.describe(name="Company name", description="Company description")
async def company(interaction: discord.Interaction, name: str, description: str):
    data["companies"].append({
        "name": name,
        "description": description
    })
    save_data()
    await interaction.response.send_message(
        embed=make_embed("🏢 WORLD BUSINESS", f"**{name}**\n{description}")
    )

@bot.tree.command(name="island", description="Register an island")
@app_commands.describe(name="Island name", ruler="Island ruler")
async def island(interaction: discord.Interaction, name: str, ruler: str):
    data["islands"].append({
        "name": name,
        "ruler": ruler
    })
    save_data()
    await interaction.response.send_message(
        embed=make_embed("🌍 ISLAND DATABASE", f"**{name}**\nRuler: {ruler}")
    )

@bot.tree.command(name="event", description="Create a world event")
@app_commands.describe(name="Event name", description="Event details")
async def event(interaction: discord.Interaction, name: str, description: str):
    data["events"].append({
        "name": name,
        "description": description,
        "date": datetime.now().isoformat()
    })
    save_data()
    await interaction.response.send_message(
        embed=make_embed(f"⚔️ {name}", description)
    )

@bot.tree.command(name="archive", description="View the news archive")
async def archive(interaction: discord.Interaction):
    entries = data["news"][-10:]
    description = "\n".join(
        f"• {item['title']}" for item in reversed(entries)
    ) or "The archive is empty."

    await interaction.response.send_message(
        embed=make_embed("📚 WORLD ECONOMY ARCHIVE", description),
        ephemeral=True
    )

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing. Add it to your environment secrets.")

bot.run(TOKEN)
