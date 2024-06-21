import discord;
import requests;
from queries.searchShow import *;
from database.userDetails import *;
from helpers.extraFunctions import *;
from helpers.embedCreator import *;

async def completedShow(score, showId, accessToken):
  mutation = """
      mutation ($mediaId: Int, $status: MediaListStatus, $score: Float) {
        SaveMediaListEntry (mediaId: $mediaId, status: $status, score: $score) {
            id
            status
            score
        }
    }
  """;

  variables = {
    "mediaId": showId,
    "status": "COMPLETED",
    "score": score
  };

  Headers = {
    "Authorization": f"Bearer {accessToken}",
    "Content-Type": "application/json",
    "Accept": "application/json",
  }

  Json = {
    "query": mutation,
    "variables": variables,
  }

  requests.post(url="https://graphql.anilist.co", headers=Headers, json=Json);

async def checkUsersList(anilistUsername, showId):
  query = """
    query ($userName: String, $animeId: Int ) { # Define which variables will be used in the query (id)
        MediaList(userName: $userName, mediaId: $animeId) {
          mediaId
          status
          score
        }
      }
  """;

  variables = {
    "userName": anilistUsername,
    "animeId": showId
  }

  Headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
  }

  Json = {
    "query": query,
    "variables": variables,
  }

  res = requests.post(url="https://graphql.anilist.co", headers=Headers, json=Json);

  if res.status_code == 200:
    body = res.json();
    mediaList = body["data"]["MediaList"];
    
    status = mediaList["status"];
    score = mediaList["score"];

    resultObj = { "found": True, "status": status, "score": score };
    return resultObj
  
  if res.status_code == 404:
    print(f"Anime or Manga not found in {anilistUsername}'s list.")
    resultObj = { "found": False };
    return resultObj

async def searchedShowEmbed(type, showTitle, showEpisodes, showCoverImage, showId, showVolumes, showChapters, score, anilistUsername, accessToken):
  await completedShow(score, showId, accessToken);

  description = f"Added {showTitle} to {anilistUsername}'s list.\nScore: {score}/10\nStatus: Completed";
  color = 0x4cfc52;

  if type == "ANIME":
    episodes = episodesCheck(showEpisodes);
    
    footerText = f"Episodes: {episodes}";
    
    embed = embedCreator(title=showTitle, description=description, color=color, imageUrl=showCoverImage, footerText=footerText);
    return embed
  
  if type == "MANGA":
    volumes = volumesCheck(showVolumes);
    chapters = chaptersCheck(showChapters);
    
    footerText = f"Volumes: {volumes}  Chapters: {chapters}";

    embed = embedCreator(title=showTitle, description=description, color=color, imageUrl=showCoverImage, footerText=footerText);
    return embed

def completedUserEmbed(type, showTitle, showEpisodes, showCoverImage, showVolumes, showChapters, score, anilistUsername, userUsername, userScore):
  description = f"Added {showTitle} to {anilistUsername}'s list.\nScore: {score}/10  {userUsername}'s Score: {userScore}/10\nStatus: Completed";
  color = 0x4cfc52;

  if type == "ANIME":
    episodes = episodesCheck(showEpisodes);
    footerText = f"Episodes: {episodes}";

    embed = embedCreator(title=showTitle, description=description, color=color, imageUrl=showCoverImage, footerText=footerText);
    return embed;

  if type == "MANGA":
    volumes = volumesCheck(showVolumes);
    chapters = chaptersCheck(showChapters);
    footerText = f"Volumes: {volumes}  Chapters: {chapters}";

    embed = embedCreator(title=showTitle, description=description, color=color, imageUrl=showCoverImage, footerText=footerText);
    return embed

async def completed_command(interaction: discord.Interaction, title, score: float, type, format):
  score = abs(score);
  if score.is_integer():
    score = int(score);
  if score > 10:
    await interaction.response.send_message("Score must be a number between 0 and 10.");
  
  completedShowSearch = await searchShowByTitle(title, type, format, interaction);
  
  if not completedShowSearch:
    await interaction.response.send_message("A problem occured when searching for the anime or manga");

  discordUserId = str(interaction.user.id)
  userDetails = getUserDetails(discordUserId);

  accessToken = userDetails["accessToken"];
  anilistUsername = userDetails["anilistUsername"];

  showTitle = completedShowSearch["title"];
  showEpisodes = completedShowSearch["episodes"];
  showCoverImage = completedShowSearch["coverImage"];
  showId = completedShowSearch["id"];
  showVolumes = completedShowSearch["volumes"];
  showChapters = completedShowSearch["chapters"];

  embed = await searchedShowEmbed(type, showTitle, showEpisodes, showCoverImage, showId, showVolumes, showChapters, score, anilistUsername, accessToken);

  await interaction.response.send_message(embeds=[embed]);

  if discordUserId == "373499146507649034":
    results = await checkUsersList("XNA", showId);
    status = results["status"];
    userScore = results["score"];

    if results["found"] and status == "COMPLETED":
      channel = await interaction.guild.fetch_channel(1180588268576849980);

      SalbtwEmbed = completedUserEmbed(type, showTitle, showEpisodes, showCoverImage, showVolumes, showChapters, score, anilistUsername, "XNA", userScore);
      
      await channel.send(embeds=[SalbtwEmbed]);

  if discordUserId == "317725955080847361":
    results = await checkUsersList("Salbtw", showId);
    status = results["status"];
    userScore = results["score"];

    if results["found"] and status == "COMPLETED":
      channel = await interaction.guild.fetch_channel(1180588268576849980);

      XNAEmbed = completedUserEmbed(type, showTitle, showEpisodes, showCoverImage, showVolumes, showChapters, score, anilistUsername, "XNA", userScore);
      
      await channel.send(embeds=[XNAEmbed]);
