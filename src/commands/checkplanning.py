import discord;
import requests;
from database.userDetails import *;
from queries.searchShow import *;
from helpers.embedCreator import *;

async def checkUserListById(username, id):
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
    "userName": username,
    "animeId": id,
  };
  
  Headers = {
      "Content-Type": "application/json",
      "Accept": "application/json",
    };
  
  Json = {
      "query": query,
      "variables": variables,
    }

  res = requests.post(url="https://graphql.anilist.co", headers=Headers, json=Json);

  if res.status_code == 200:
    data = res.json();
    mediaList = data["data"]["MediaList"];

    id = mediaList["mediaId"];
    status = mediaList["status"];
    score = mediaList["score"];
    
    results = {
      "id": id,
      "status": status,
      "score": score
    }

    return results;
    
  if res.status_code == 404:
    status = f"Not found in {username}'s Anilist";
    obj = {
      "status": status
    }
    return obj;

async def checkPlanning(title, type, format, discordUserId, interaction: discord.Interaction):
  userDetails = getUserDetails(discordUserId);
  
  if "Error" in userDetails:
    err = userDetails["Error"];
    return None;

  if "anilistUsername" in userDetails:
    anilistUsername = userDetails["anilistUsername"];
    
    showDetails = await searchShowByTitle(title, type, format, interaction, True);

    showId = showDetails["id"];

    results = await checkUserListById(anilistUsername, showId);
    status = results["status"];
    
    showInfo = {
      "showDetails": showDetails,
      "status": status,
      "anilistUsername": anilistUsername
    }

    return showInfo;

def checkPlanningEmbed(showTitle, coverImage, status, anilistUsername, type):
  if status == "PLANNING":
    if type == "ANIME":
      description = f"{anilistUsername} is Planning to watch {showTitle}";
      color = 0xdf4cfc;

      embed = embedCreator(title=showTitle, description=description, color=color, imageUrl=coverImage);
      return embed;
    
    if type == "MANGA":
      description = f"{anilistUsername} is Planning to read {showTitle}";
      color = 0xdf4cfc;

      embed = embedCreator(title=showTitle, description=description, color=color, imageUrl=coverImage);
      return embed;
  else:
    description = f"{showTitle} is not in {anilistUsername}'s Planning List";
    color = 0xff5542;

    embed = embedCreator(title=showTitle, description=description, color=color, imageUrl=coverImage);
    return embed;

async def checkplanning_command(interaction: discord.Interaction, title, type, format, user: discord.user.User):
  if user.bot:
      await interaction.followup.send(f"{user.display_name} is not a user. Please enter a valid user in the user field.");
      return
  
  discordUserId = str(user.id);

  showInfo = await checkPlanning(title, type, format, discordUserId, interaction);

  if showInfo == None:
    await interaction.followup.send(f"{user.display_name} is not authenticated. Please enter an authenticated user in the user field");
    return
  
  showTitle = showInfo["showDetails"]["title"];
  coverImage = showInfo["showDetails"]["coverImage"];
  status = showInfo["status"];
  anilistUsername = showInfo["anilistUsername"];

  embed = checkPlanningEmbed(showTitle, coverImage, status, anilistUsername, type)

  await interaction.followup.send(embeds=[embed]);