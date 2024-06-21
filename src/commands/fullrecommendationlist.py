import discord;
from database.userDetails import *;
from database.recDetails import *;
from queries.searchShow import *;
from helpers.extraFunctions import *;
from helpers.embedCreator import *;
from helpers.buttons import *;

def createDescription(anilistUsername, genre, type, format):
  if type == "ANIME":
    description = f"{anilistUsername}'s Full Recommendation list. \nGenre: {genre} \nType: {type.capitalize()} \nFormat: {format}";
  if type == "MANGA":
    description = f"{anilistUsername}'s Full Recommendation list. \nGenre: {genre} \nType: {type.capitalize()}";
  return description;

def createFooterText(type, episodes, volumes, chapters, currentIndex, totalShows):
  if type == "ANIME":
    footerText = f"Episodes: {episodes} | Page {currentIndex + 1}/{totalShows}";
  if type == "MANGA":
    footerText = f"Volumes: {volumes}  Chapters: {chapters} | Page {currentIndex + 1}/{totalShows}";
  return footerText

def getCurrentEmbed(self):
  newList = self.List[self.currentIndex];
  title = newList["showData"]["title"];
  genre = newList["genre"];
  episodes = episodesCheck(newList["showData"]["episodes"]);
  chapters = chaptersCheck(newList["showData"]["chapters"]);
  volumes = volumesCheck(newList["showData"]["volumes"]);
  format = newList["showData"]["format"];
  type = newList["showData"]["type"];
  color = self.format["color"];
  imageUrl = newList["showData"]["coverImage"];
  anilistUsername = self.format["anilistUsername"];
  description = self.createDescription(anilistUsername, genre, type, format);
  currentIndex = self.currentIndex;
  totalShows = self.format["totalShows"];
  footerText = self.createFooterText(type, episodes, volumes, chapters, currentIndex, totalShows);

  embed = embedCreator(title=title, description=description, color=color, imageUrl=imageUrl, footerText=footerText);
  return embed;

def createEmbed(data, anilistUsername):
  for show in data:
    index = data.index(show);
    genre = show["genre"];
    title = show["showData"]["title"];
    episodes = episodesCheck(show["showData"]["episodes"]);
    chapters = chaptersCheck(show["showData"]["chapters"]);
    volumes = volumesCheck(show["showData"]["volumes"]);
    coverImage = show["showData"]["coverImage"];
    format = show["showData"]["format"];
    id = show["showData"]["id"];
    type = show["showData"]["type"];

    currentIndex = index;
    totalShows = len(data);

    color = 0xff9130;
    imageUrl = coverImage;

    if type == "ANIME":
      description = f"{anilistUsername}'s Full Recommendation list. \nGenre: {genre} \nType: {type.capitalize()} \nFormat: {format}";
      footerText = f"Episodes: {episodes} | Page {currentIndex + 1}/{totalShows}";

    if type == "MANGA":
      description = f"{anilistUsername}'s Full Recommendation list. \nGenre: {genre} \nType: {type.capitalize()}";
      footerText = f"Volumes: {volumes}  Chapters: {chapters} | Page {currentIndex + 1}/{totalShows}";

    Format = { "color": color, "totalShows": totalShows, "anilistUsername": anilistUsername };

    embed = embedCreator(title=title, description=description, color=color, imageUrl=imageUrl, footerText=footerText);
    return { "embed": embed, "index": index, "format": Format };

async def orderData(data, type):
  orderedData = []
  for obj in data:
    genre = obj["genre"];
    title = obj["title"];
    showId = obj["showId"];
    results = await searchShowById(showId, type);
    orderedData.append({ "genre": genre, "showData": results });
  return orderedData;

async def fullrecommendationlist_command(interaction: discord.Interaction, type):
  discordUserId = str(interaction.user.id);

  userDetails = getUserDetails(discordUserId);

  if "Error" in userDetails:
    err = userDetails["Error"];
    await interaction.followup.send("You are not authenticated");
    return
  
  anilistUsername = userDetails["anilistUsername"];

  fullRecData = await fullRecDetails(anilistUsername, type);

  if len(fullRecData) == 0:
    type = type.capitalize();
    await interaction.followup.send(f"You don't have any **{type}** recommended");
    return

  data = await orderData(fullRecData, type);
  
  emebd = createEmbed(data, anilistUsername)["embed"];
  currentIndex = createEmbed(data, anilistUsername)["index"];
  Format = createEmbed(data, anilistUsername)["format"];

  fullRecFormat = { "list": data, "format": Format };

  btn = create_button(fullRecFormat, currentIndex, emebd, createDescription, getCurrentEmbed, createFooterText);
  await interaction.followup.send(embeds=[emebd], view=btn);