import discord;
from queries.searchShow import *;
from database.userDetails import *;
from helpers.embedCreator import *;
from helpers.extraFunctions import *;
from database.recDetails import *;

def delRecShowEmbed(showTitle, showEpisodes, showCoverImage, showVolumes, showChapters, anilistUsername, genre, type):
  if type == "ANIME":
    type = type.capitalize();
    episodes = episodesCheck(showEpisodes);
    footerText = f"Episodes: {episodes}"

    description = f"Deleted {showTitle} from {anilistUsername}'s Recommend list.\nGenre: {genre} \nType: {type}";
    color = 0xe62020;

    embed = embedCreator(title=showTitle, description=description, imageUrl=showCoverImage,  color=color, footerText=footerText);
    return embed
  
  if type == "MANGA":
    type = type.capitalize();
    volumes = volumesCheck(showVolumes);
    chapters = chaptersCheck(showChapters);
    footerText = f"Volumes: {volumes}  Chapters: {chapters}";

    description = f"Deleted {showTitle} from {anilistUsername}'s Recommend list.\nGenre: {genre} \nType: {type}";
    color = 0xe62020;

    embed = embedCreator(title=showTitle, description=description, imageUrl=showCoverImage, color=color, footerText=footerText);
    return embed

async def userDelRec(userUsername, genre, showTitle, type, interaction):
  title = showTitle;
  type = type.capitalize();
  result = await delRec(userUsername, type, genre, title)

  return result;

async def deleterecommendation_command(interaction: discord.Interaction, title, type, format, genre):
  discordUserId = str(interaction.user.id);

  delRecShowSearch = await searchShowByTitle(title, type, format, interaction);

  if not delRecShowSearch:
    # await interaction.response.send_message("A problem occured when searching for the anime or manga");
    return
  
  userDetails = getUserDetails(discordUserId);
  anilistUsername = userDetails["anilistUsername"];

  showTitle = delRecShowSearch["title"];
  showEpisodes = delRecShowSearch["episodes"];
  showCoverImage = delRecShowSearch["coverImage"];
  showVolumes = delRecShowSearch["volumes"];
  showChapters = delRecShowSearch["chapters"];

  embed = delRecShowEmbed(showTitle, showEpisodes, showCoverImage, showVolumes, showChapters, anilistUsername, genre, type);

  if discordUserId == "317725955080847361":
    result = await userDelRec("XNA", genre, showTitle, type, interaction);

  if discordUserId == "373499146507649034":
    result = await userDelRec("Salbtw", genre, showTitle, type, interaction);

  if result == False:
    await interaction.response.send_message(f"It appears that this {type.capitalize()} is not in your **{genre}** recommendation list.");
    return
  else:
    await interaction.response.send_message(embeds=[embed]);