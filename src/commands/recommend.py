import discord;
from queries.searchShow import *;
from database.userDetails import *;
from helpers.extraFunctions import *;
from helpers.embedCreator import *;
from database.recDetails import *;

def recommendShowEmbed(showTitle, showEpisodes, showCoverImage, showVolumes, showChapters, anilistUsername, genre, type):
  if type == "ANIME":
    type = capitalizeFirstLetter(type);
    episodes = episodesCheck(showEpisodes);
    footerText = f"Episodes: {episodes}"

    description = f"Added {showTitle} to {anilistUsername}'s Recommend list.\nGenre: {genre} \nType: {type}";
    color = 0xff9130;

    embed = embedCreator(title=showTitle, description=description, imageUrl=showCoverImage,  color=color, footerText=footerText);
    return embed
  
  if type == "MANGA":
    type = capitalizeFirstLetter(type);
    volumes = volumesCheck(showVolumes);
    chapters = chaptersCheck(showChapters);
    footerText = f"Volumes: {volumes}  Chapters: {chapters}";

    description = f"Added {showTitle} to {anilistUsername}'s Recommend list.\nGenre: {genre} \nType: {type}";
    color = 0xff9130;

    embed = embedCreator(title=showTitle, description=description, imageUrl=showCoverImage, color=color, footerText=footerText);
    return embed

async def userStoreRecommendation(userUsername, genre, showTitle, showId, type):
  title = showTitle;
  type = capitalizeFirstLetter(type);
  await addRec(userUsername, type, genre, title, showId)

async def recommend_command(interaction: discord.Interaction, title, type, format, genre):
  discordUserId = str(interaction.user.id);

  recommendShowSearch = await searchShowByTitle(title, type, format, interaction, True)

  if not recommendShowSearch:
    # await interaction.response.send_message("A problem occured when searching for the anime or manga");
    return
  
  userDetails = getUserDetails(discordUserId);
  anilistUsername = userDetails["anilistUsername"];
  
  showTitle = recommendShowSearch["title"];
  showEpisodes = recommendShowSearch["episodes"];
  showCoverImage = recommendShowSearch["coverImage"];
  showId = recommendShowSearch["id"];
  showVolumes = recommendShowSearch["volumes"];
  showChapters = recommendShowSearch["chapters"];

  embed = recommendShowEmbed(showTitle, showEpisodes, showCoverImage, showVolumes, showChapters, anilistUsername, genre, type);

  if discordUserId == "317725955080847361":
    await userStoreRecommendation("XNA", genre, showTitle, showId, type);

  if discordUserId == "373499146507649034":
    await userStoreRecommendation("Salbtw", genre, showTitle, showId, type);

  await interaction.followup.send(embeds=[embed]);