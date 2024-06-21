import discord;
from helpers.extraFunctions import *;
from helpers.embedCreator import *;
from helpers.buttons import *;
from database.recDetails import *;
from database.userDetails import *;
from queries.searchShow import *;

def createDescription(type, anilistUsername, genre, format):
  if type == "ANIME":
      description = f"{anilistUsername}'s Recommended list. \nGenre: {genre} \nType: {type.capitalize()} \nformat: {format}";

  if type == "MANGA":
      description = f"{anilistUsername}'s Recommended list. \nGenre: {genre} \nType: {type.capitalize()}";

  return description

def createFooterText(type, episodes, volumes, chapters, currentIndex, totalShows):
  if type == "ANIME":
    footerText = f"Episodes: {episodes} | Page {currentIndex + 1}/{totalShows}";

  if type == "MANGA":
    footerText = f"Volumes: {volumes}  Chapters: {chapters} | Page {currentIndex + 1}/{totalShows}";

  return footerText

def getCurrentEmbed(self):
  newList = self.List[self.currentIndex];
  title = newList["title"];
  type = self.format["type"];
  genre = self.format["genre"];
  format = newList["format"];
  episodes = episodesCheck(newList["episodes"]);
  volumes = volumesCheck(newList["volumes"]);
  chapters = chaptersCheck(newList["chapters"]);
  color = self.format["color"];
  imageUrl = newList["coverImage"];
  anilistUsername = self.format["anilistUsername"];
  description = self.createDescription(type, anilistUsername, genre, format);
  totalShows = self.format["totalShows"];
  currentIndex = self.currentIndex;
  footerText = self.createFooterText(type, episodes, volumes, chapters, currentIndex, totalShows);

  embed = embedCreator(title=title, description=description, color=color, imageUrl=imageUrl, footerText=footerText);
  return embed

async def getShows(reclist: dict, type: str):
  type = type.upper();
  showIdsArray = [];
  showsArray = [];
  # print(reclist)
  for _, showIds in reclist.items():
    showIdsArray.append(showIds);

  for showId in showIdsArray:
    resultObj = await searchShowById(showId, type);
    showsArray.append(resultObj);

  return showsArray

def createRecListEmbed(shows: list, type: str, genre,  user: discord.user.User, interaction):
  discordUserId = str(user.id)
  anilistUsername = getUserDetails(discordUserId)["anilistUsername"];
  type = type.upper();
  for show in shows:
    index = shows.index(show);
    title = show["title"];
    episodes = episodesCheck(show["episodes"]);
    chapters = chaptersCheck(show["chapters"]);
    volumes = volumesCheck(show["volumes"]);
    coverImage = show["coverImage"];
    format = show["format"];
    id = show["id"];

    currentIndex = index;
    totalShows = len(shows);

    color = 0xff9130
    imageUrl = coverImage;

    Format = { "color": color, "totalShows": totalShows, "type": type, "genre": genre, "anilistUsername": anilistUsername }
 
    if type == "ANIME":
      description = f"{anilistUsername}'s Recommended list. \nGenre: {genre} \nType: {type.capitalize()} \nformat: {format}"
      footerText = f"Episodes: {episodes} | Page {currentIndex + 1}/{totalShows}"

      embed = embedCreator(title=title, description=description, color=color, imageUrl=imageUrl, footerText=footerText);
    
    if type == "MANGA":
      description = f"{anilistUsername}'s Recommended list. \nGenre: {genre} \nType: {type.capitalize()}"
      footerText = f"Volumes: {volumes}  Chapters: {chapters} | Page {currentIndex + 1}/{totalShows}"

      embed = embedCreator(title=title, description=description, color=color, imageUrl=imageUrl, footerText=footerText);
    return { "embed": embed, "index": index, "format": Format }

async def recommendlist_command(interaction: discord.Interaction, type, genre, user: discord.user.User):
  type = capitalizeFirstLetter(type);
  username = interaction.user.global_name;
  
  if user:
    if user.bot:
      await interaction.followup.send(f"{user.display_name} is not a user. Please enter a valid user in the user field.");
      return
    elif user:
      username = user.global_name;
    else:
      await interaction.followup.send("Please enter a valid user in the user field.");
      return
  else:
    user = interaction.user

  reclist = await recDetails(username, type, genre);
  
  if reclist == None:
    if user:
      await interaction.followup.send(f"{username} doesn't have a recommendation list");
      return
    else:
      await interaction.followup.send("You don't have a recommendation list");
      return
  if reclist == {}:
    await interaction.followup.send("This recommendation list is empty.");
    return
  
  shows = await getShows(reclist, type);

  embed = createRecListEmbed(shows, type, genre, user, interaction)["embed"];
  currentIndex = createRecListEmbed(shows, type, genre, user, interaction)["index"];
  Format = createRecListEmbed(shows, type, genre, user, interaction)["format"];

  showsFormat = { "list": shows, "format": Format };
  # print(shows)

  btn = create_button(showsFormat, currentIndex, embed, createDescription, getCurrentEmbed, createFooterText);
  await interaction.followup.send(embeds=[embed], view=btn)

  # if user:
  #   await interaction.response.send_message(f"Type: {type}, Genre: {genre}, User: {user}");
  # else:
  #   await interaction.response.send_message(f"Type: {type}, Genre: {genre}");