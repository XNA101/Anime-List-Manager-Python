import discord;
import requests;
import asyncio;
from database.userDetails import *;
from queries.searchShow import *;
from helpers.extraFunctions import *;
from helpers.embedCreator import *;

def fixShowInfo(list, show, episode, end, animeTitle):
  showId = show["id"];
  episodes = show["episodes"];
  if show["status"] == "RELEASING":
    lastEpisode = show["nextEpisode"] - 1;
  
  for media in list:
    if showId == media["id"]:
      status = media["status"];
      if status == "COMPLETED":
        return { "status": "Completed Alredy", "response": f"You have already completed **{animeTitle}**" }
      progress = media["progress"];
      if end and end < episode or end == 0:
        return { "status": "End is less than Episode", "response": f"**End ({end}) is less than Episode ({episode})**. Please Make sure that End is greater than Episode" }
      elif episode < progress:
        return { "status": "Below", "response": f"**{animeTitle} Ep.{progress}** was the last Episode you watched. You're Trying to update Episode **{episode}**" }
      elif episode == progress:
        return { "status": "Episode Equal", "response": f"You have already updated **Ep.{progress}** of **{animeTitle}**" }
      elif episodes and episode > episodes:
        return { "status": "Episode Above", "response": f"**{animeTitle}** has only **{episodes}** Episodes. You're trying to update it to **{episode}** Episodes" }
      elif end and episodes and  end > episodes:
        return { "status": "End Above", "response": f"**{animeTitle}** has only **{episodes}** Episodes. You're trying to update it to **{end}** Episodes" }
      elif show["status"] == "RELEASING" and episode > lastEpisode:
        return { "status": "Episode Above Released Episodes", "response": f"Only **{lastEpisode}** Episodes have been realeased of **{animeTitle}**. You're trying to update it to **{episode}** Episodes" }
      elif show["status"] == "RELEASING" and end and end > lastEpisode:
        return { "status": "End Above Released Episodes", "response": f"Only **{lastEpisode}** Episodes have been realeased of **{animeTitle}**. You're trying to update it to **{end}** Episodes" }
      else:
        return { "status": "Alright" }
      
  if end and end < episode or end == 0:
    return { "status": "End is less than Episode", "response": f"**End ({end}) is less than Episode ({episode})**. Please Make sure that End is greater than Episode" }
  elif episodes and episode > episodes:
    return { "status": "Episode Above", "response": f"**{animeTitle}** has only **{episodes}** Episodes. You're trying to update it to **{episode}** Episodes" }
  elif end and episodes and  end > episodes:
    return { "status": "End Above", "response": f"**{animeTitle}** has only **{episodes}** Episodes. You're trying to update it to **{end}** Episodes" }
  elif show["status"] == "RELEASING" and episode > lastEpisode:
    return { "status": "Episode Above Released Episodes", "response": f"Only **{lastEpisode}** Episodes have been realeased of **{animeTitle}**. You're trying to update it to **{episode}** Episodes" }
  elif show["status"] == "RELEASING" and end and end > lastEpisode:
    return { "status": "End Above Released Episodes", "response": f"Only **{lastEpisode}** Episodes have been realeased of **{animeTitle}**. You're trying to update it to **{end}** Episodes" }
  else:
    return { "status": "Alright" }

# def checkIfShowIsCurrent(list, show):
  idsArray = [];
  for media in list:
    title = media["title"];
    id = media["id"];
    idsArray.append(id);

  showid = show["id"];
  
  if showid in idsArray:
    return True
  else:
    return False

def checkProgressEqual(progress, episode, end = None):
  if end and end <= progress:
    return True
  elif end and end != progress:
    return False 
  elif episode <= progress:
    return True
  if episode != progress:
    return False

async def updateUserList(showId, progress, discordUserId):
  userData = getUserDetails(discordUserId);

  if userData:
     accessToken = userData["accessToken"];
  
  mutation = """
    mutation ($mediaId: Int, $progress: Int, $status: MediaListStatus) {
        SaveMediaListEntry (mediaId: $mediaId, progress: $progress, status: $status) {
            id
            progress
            status
        }
    }
  """;

  variables = {
    "mediaId": showId,
    "progress": progress,
    "status": "CURRENT"
  }

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
          progress
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
    progress = mediaList["progress"];

    resultObj = { "found": True, "status": status, "progress": progress };
    return resultObj
  
  if res.status_code == 404:
    resultObj = { "found": False };
    return resultObj

async def watchedEmbed(show, episode, end, discordUserId):
  title = show["title"];

  if end:
    description = f"Watched **Ep.{episode}-Ep.{end}** of **{title}**";
  else:
    description = f"Watched **Ep.{episode}** of **{title}**";
  
  if end and end == show["episodes"]:
    color = 0x4cfc52;
  elif episode == show["episodes"]:
    color = 0x4cfc52;
  else:
    color = 0x4ccafc;
  
  coverImage = show["coverImage"];
  id = show["id"];
  status = show["status"];
  episodes = episodesCheck(show["episodes"]);
  footerText = f"Episodes: {episodes}"
  
  await updateUserList(id, episode, discordUserId)
  if end:
    await asyncio.sleep(1.5)
    await updateUserList(id, end, discordUserId)

  embed = embedCreator(title=title, description=description, color=color, imageUrl=coverImage, footerText=footerText);
  return { "embed": embed, "status": status }

async def userWatchedEmbed(show, episode, end, discordUserId):
  userData = getUserDetails(discordUserId);

  if userData:
      anilistUsername = userData["anilistUsername"];

  title = show["title"];

  if end:
    description = f"{anilistUsername} Watched **Ep.{episode}-Ep.{end}** of **{title}** ";
  else:
    description = f"{anilistUsername} Watched **Ep.{episode}** of **{title}**";
  
  color = 0x7542f5;
  
  coverImage = show["coverImage"];
  episodes = episodesCheck(show["episodes"]);
  footerText = f"Episodes: {episodes}"

  embed = embedCreator(title=title, description=description, color=color, imageUrl=coverImage, footerText=footerText);
  return embed

async def getUserAnimeList(discordUserId):
  try:
    userData = getUserDetails(discordUserId);
  
    if userData:
      accessToken = userData["accessToken"];
      anilistUsername = userData["anilistUsername"];
      
      query = """
      query ($userName: String, $type: MediaType, $sort: [MediaListSort]) { # Define which variables will be used in the query (id)
        MediaListCollection (userName: $userName, type: $type, sort: $sort) {
          user {
            name
          }
          lists {
            entries {
              media {
                title {
                  userPreferred
                }
                id
              }
              progress
            }
            status
          }
        }
      }""";
  
      variables =  {
        "userName": anilistUsername,
        "type": "ANIME",
        "sort": "UPDATED_TIME_DESC",
      };

      Headers = {
          "Authorization": "Bearer " + accessToken,
          "Content-Type": "application/json",
          "Accept": "application/json",
        }
      
      Json = {
          "query": query,
          "variables": variables,
        }
  
      res = requests.post(url="https://graphql.anilist.co", headers=Headers, json=Json);
      
      if res.status_code == 200:
        data = res.json();

        userName = data["data"]["MediaListCollection"]["user"]["name"];
        lists = data["data"]["MediaListCollection"]["lists"]
        results = []
        for List in lists:
          status = List["status"];
          entries = List["entries"];
          for entry in entries:
            title = entry["media"]["title"]["userPreferred"];
            id = entry["media"]["id"];
            progress = entry["progress"];
            
            data = {
              "title": title,
              "id": id,
              "progress": progress,
              "status": status
            };

            results.append(data);

    return results
    
  except:
    print("There was a problem with the getUserAnimeList function")

async def watched_command(interaction: discord.Interaction, title, format, episode, end):
  discordUserId = str(interaction.user.id);
  animeList = await getUserAnimeList(discordUserId);
  anime = await searchShowByTitle(title, "ANIME", format, interaction, True);
  # print(anime);

  if not anime:
    return
  
  animeTitle = anime["title"];
  animeId = anime["id"];
  # checkResult = checkIfShowIsCurrent(animeList, anime);

  fixResults = fixShowInfo(animeList, anime, episode, end, animeTitle);
  # print(fixResults)

  if fixResults and fixResults["status"] != "Alright":
    res = fixResults["response"];
    await interaction.followup.send(res);
    return
  
  weResult = await watchedEmbed(anime, episode, end, discordUserId);
  embed = weResult["embed"];
  status = weResult["status"];

  await interaction.followup.send(embeds=[embed]);

  if status == "RELEASING":
    if discordUserId == "317725955080847361":
      results = await checkUsersList("Salbtw", animeId);
      if results["found"] and results["status"] == "CURRENT":
        progress = results["progress"]
        isProgressEqual = checkProgressEqual(progress, episode, end)
        if isProgressEqual:
          channel = await interaction.guild.fetch_channel(1180588268576849980);
          embed = await userWatchedEmbed(anime, episode, end, discordUserId);
          await channel.send(embeds=[embed])

    if discordUserId == "373499146507649034":
      results = await checkUsersList("XNA", animeId);
      if results["found"] and results["status"] == "CURRENT":
        progress = results["progress"]
        isProgressEqual = checkProgressEqual(progress, episode, end)
        if isProgressEqual:
          channel = await interaction.guild.fetch_channel(1180588268576849980);
          embed = await userWatchedEmbed(anime, episode, end, discordUserId);
          await channel.send(embeds=[embed])

