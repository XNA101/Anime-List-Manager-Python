import discord;
from discord import app_commands;
from dotenv import load_dotenv;
import os;
import logging;
from commands.allcommands import *;
from db import *;
from typing import Optional;
import asyncio;

load_dotenv();
TOKEN = os.getenv("TOKEN");

intents = discord.Intents.all();

client = discord.Client(intents=intents);
interaction = discord.Interaction;
tree = app_commands.CommandTree(client)
Choice = app_commands.Choice;

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w");

@tree.command(name="animelist", description="Shows the user's Anime list")
@app_commands.describe(status="Shows the user's Anime list", page="What page do you want to start at?")
@app_commands.choices(status=status_choices)
async def animelist(interaction, status: str, page: int = None):
  await animelist_command(interaction, status, page);


@tree.command(name="mangalist", description="Shows the user's Manga list")
@app_commands.describe(status="Shows the user's Manga list", page="What page do you want to start at?")
@app_commands.choices(status=status_choices)
async def mangalist(interaction, status: str, page: int = None):
  await mangalist_command(interaction, status, page);

@tree.command(name="search", description="Search for an Anime or Manga")
@app_commands.describe(title="Anime title", type="Anime or Manga", format="Format of the Media")
@app_commands.choices(type=type_choices, format=format_choices)
async def search(interaction, title: str, type: str, format: str):
  await search_command(interaction, title, type, format);

@tree.command(name="completed", description="Adds an Anime or Manga to your list as Completed")
@app_commands.describe(title="Show title", score="Rating out of 10", type="Anime or Manga", format="Format of the Media")
@app_commands.choices(type=type_choices, format=format_choices)
async def completed(interaction, title: str, score: float, type: str, format: str):
  await completed_command(interaction, title, score, type, format);

@tree.command(name="recommend", description="Recommend an Anime or a Manga")
@app_commands.describe(title="Show title", type="Anime or Manga", format="Format of the Media", genre="Genre of the Anime or Manga")
@app_commands.choices(type=type_choices, format=format_choices, genre=genre_choices)
async def recommend(interaction, title: str, type: str, format: str, genre: str):
  await recommend_command(interaction, title, type, format, genre);

@tree.command(name="recommendlist", description="List of Recommended Anime or Manga")
@app_commands.describe(type="Anime or Manga", genre="Genre of the Anime or Manga", user="user")
@app_commands.choices(type=type_choices, genre=genre_choices)
async def recommendlist(interaction: discord.Interaction, type: str,  genre: str, user: discord.user.User = None):
  await interaction.response.defer();
  await recommendlist_command(interaction, type, genre, user);

@tree.command(name="deleterecommendation", description="Delete a Recommendation of Anime or Manga from your Recommendation List")
@app_commands.describe(title="Show title", type="Anime or Manga", format="Format of the Media", genre="Genre of the Anime or Manga")
@app_commands.choices(type=type_choices, format=format_choices, genre=genre_choices)
async def deleterecommendation(interaction, title: str, type: str, format: str, genre: str):
  await deleterecommendation_command(interaction, title, type, format, genre);

@tree.command(name="checkplanning", description="Check's if an animanga is in a user's planning list")
@app_commands.describe(title="Show title", type="Anime or Manga", format="Format of the Media", user="user")
@app_commands.choices(type=type_choices, format=format_choices)
async def checkplanning(interaction: discord.Interaction, title: str, type: str, format: str, user: discord.user.User):
  await checkplanning_command(interaction, title, type, format, user);

@tree.command(name="fullrecommendationlist", description="Show the full recommendation list of the user")
@app_commands.describe(type="Anime or Manga")
@app_commands.choices(type=type_choices)
async def fullrecommendationlist(interaction: discord.Interaction, type: str):
  await interaction.response.defer();
  await fullrecommendationlist_command(interaction, type);

@client.event
async def on_ready():
  await tree.sync()
  print(f"✅ {client.user} is online");

 
client.run(TOKEN, log_handler= handler);
