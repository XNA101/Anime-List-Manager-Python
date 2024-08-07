import discord;
from helpers.extraFunctions import *;
from helpers.embedCreator import *;
from queries.searchShow import *;

def searchedShowEmbed(type, title, description, episodes, coverImage, volumes, chapters):
  if type == "ANIME":

    footerText = f"Episodes: {episodesCheck(episodes)}";

    embed = embedCreator(title=title, description=description, color=0x524cfc, imageUrl=coverImage, footerText=footerText);
    return embed;

  if type == "MANGA":
    if description != None:
      cleanDescription = stripHtmlTags(description);
    else:
      cleanDescription = "No Description";
    footerText = f"Volumes: {volumesCheck(volumes)}  Chapters: {chaptersCheck(chapters)}";

    embed = embedCreator(title=title, description=cleanDescription, color=0x524cfc, imageUrl=coverImage, footerText=footerText);
    return embed

async def search_command(interaction: discord.Interaction, title: str, type: str, format: str):
  show = await searchShowByTitle(title, type, format, interaction, True);
  
  if not show:
  #   await interaction.response.send_message("A problem occurred when searching for the anime or manga");
    return
  
  embed = searchedShowEmbed(type, show["title"], show["description"], show["episodes"], show["coverImage"], show["volumes"], show["chapters"]);

  if embed:
    await interaction.followup.send(embeds=[embed]);
  else:
    await interaction.followup.send("An error occurred while processing your request.")