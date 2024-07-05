import discord;
import requests;
import asyncio;
from database.userDetails import *;
from queries.searchShow import *;
from helpers.extraFunctions import *;
from helpers.embedCreator import *;

def fixShowInfo(list, show, chapter, chend, volume, vend, mangaTitle):
  showId = show["id"];
  chapters = show["chapters"];
  volumes = show["volumes"];

  for media in list:
    if showId == media["id"]:
      status = media["status"];
      if status == "COMPLETED":
        return { "status": "Completed Alredy", "response": f"You have already completed **{mangaTitle}**" }
      progress = media["progress"];
      progressVolumes = media["progressVolumes"];
      if chend and chend < chapter or chend == 0:
        return { "status": "ChEnd is less than Chapter", "response": f"**ChEnd ({chend}) is less than Chapter ({chapter})**. Please Make sure that ChEnd is greater than Chapter" }
      elif vend and not volume:
        return { "status": "Vend provided but no Volume", "response": f"Value for Vend (**{vend}**) was provided but no value was provided for the Volume field." }
      elif volume and vend and vend < volume or vend == 0:
        return { "status": "VEnd is less than Volume", "response": f"**VEnd ({vend}) is less than Volume ({volume})**. Please Make sure that VEnd is greater than Volume" }
      elif chapter < progress:
        return { "status": "Chapter Below", "response": f"**{mangaTitle} Ch.{progress}** was the last Chapter you read. You're Trying to update Chapter **{chapter}**" }
      elif chapter == progress:
        return { "status": "Chapter Equal", "response": f"You have already updated **Ch.{progress}** of **{mangaTitle}**" }
      elif chapters and chapter > chapters:
        return { "status": "Chapter Above", "response": f"**{mangaTitle}** has only **{chapters}** Chapters. You're trying to update it to **{chapter}** Chapters" }
      elif chend and chapters and  chend > chapters:
        return { "status": "ChEnd Above", "response": f"**{mangaTitle}** has only **{chapters}** Chapters. You're trying to update it to **{chend}** Chapters" }
      elif volume and volume < progressVolumes:
        return { "status": "Volume Below", "response": f"**{mangaTitle} Vol.{progressVolumes}** was the last Volume you read. You're Trying to update Volume **{volume}**" }
      elif volume and volume == progressVolumes:
        return { "status": "Volume Equal", "response": f"You have already updated **Vol.{progressVolumes}** of **{mangaTitle}**" }
      elif volume and volumes and volume > volumes:
        return { "status": "Volume Above", "response": f"**{mangaTitle}** has only **{volumes}** Volumes. You're trying to update it to **{volume}** Volumes" }
      elif vend and volumes and vend > volumes:
        return { "status": "VEnd Above", "response": f"**{mangaTitle}** has only **{volumes}** Volumes. You're trying to update it to **{vend}** Volumes" }
      else:
        return { "status": "Alright" }
      
  if chend and chend < chapter or chend == 0:
    return { "status": "ChEnd is less than Chapter", "response": f"**ChEnd ({chend}) is less than Chapter ({chapter})**. Please Make sure that ChEnd is greater than Chapter" }
  elif vend and not volume:
    return { "status": "Vend provided but no Volume", "response": f"Value for Vend (**{vend}**) was provided but no value was provided for the Volume field." }
  elif volume and vend and vend < volume or vend == 0:
    return { "status": "VEnd is less than Volume", "response": f"**VEnd ({vend}) is less than Volume ({volume})**. Please Make sure that VEnd is greater than Volume" }
  elif chapters and chapter > chapters:
    return { "status": "Chapter Above", "response": f"**{mangaTitle}** has only **{chapters}** Chapters. You're trying to update it to **{chapter}** Chapters" }
  elif chend and chapters and  chend > chapters:
    return { "status": "ChEnd Above", "response": f"**{mangaTitle}** has only **{chapters}** Chapters. You're trying to update it to **{chend}** Chapters" }
  elif volume and volumes and volume > volumes:
    return { "status": "Volume Above", "response": f"**{mangaTitle}** has only **{volumes}** Volumes. You're trying to update it to **{volume}** Volumes" }
  elif vend and volumes and vend > volumes:
    return { "status": "VEnd Above", "response": f"**{mangaTitle}** has only **{volumes}** Volumes. You're trying to update it to **{vend}** Volumes" }
  else:
    return { "status": "Alright" }

def checkProgressEqual(progress, chapter, chend = None):
  if chend and chend <= progress:
    return True
  elif chend and chend != progress:
    return False 
  elif chapter <= progress:
    return True
  if chapter != progress:
    return False

async def updateUserList(showId, discordUserId, progress = None, progressVolumes = None):
  userData = getUserDetails(discordUserId);

  if userData:
     accessToken = userData["accessToken"];
  
  if progress and progressVolumes:
    mutation = """
      mutation ($mediaId: Int, $progress: Int, $progressVolumes: Int, $status: MediaListStatus) {
          SaveMediaListEntry (mediaId: $mediaId, progress: $progress, progressVolumes: $progressVolumes, status: $status) {
              id
              progress
              progressVolumes
              status
          }
      }
    """;

    variables = {
      "mediaId": showId,
      "progress": progress,
      "progressVolumes": progressVolumes,
      "status": "CURRENT"
    }
  elif progress:
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
  elif progressVolumes:
    mutation = """
      mutation ($mediaId: Int, $progressVolumes: Int, $status: MediaListStatus) {
          SaveMediaListEntry (mediaId: $mediaId, progressVolumes: $progressVolumes, status: $status) {
              id
              progressVolumes
              status
          }
      }
    """;

    variables = {
      "mediaId": showId,
      "progressVolumes": progressVolumes,
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
          progressVolumes
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
    progressVolumes = mediaList["progressVolumes"];

    resultObj = { "found": True, "status": status, "progress": progress, "progressVolumes": progressVolumes };
    return resultObj
  
  if res.status_code == 404:
    resultObj = { "found": False };
    return resultObj

async def readEmbed(show, chapter, chend, volume, vend, discordUserId):
  title = show["title"];

  if chend and volume and vend:
    description = f"Read **Ch.{chapter}-Ch.{chend}** and **Vol.{volume}-Vol.{vend}** of **{title}**";
  elif chend and volume:
    description = f"Read **Ch.{chapter}-Ch.{chend}** and **Vol.{volume}** of **{title}**";
  elif chend:
    description = f"Read **Ch.{chapter}-Ch.{chend}** of **{title}**";
  elif volume and vend:
    description = f"Read **Ch.{chapter}** and **Vol.{volume}-Vol.{vend}** of **{title}**";
  elif volume:
    description = f"Read **Ch.{chapter}** and **Vol.{volume}** of **{title}**";
  else:
    description = f"Read **Ch.{chapter}** of **{title}**";
  
  if chend and chend == show["chapters"]:
    color = 0x4cfc52;
  elif chapter == show["chapters"]:
    color = 0x4cfc52;
  else:
    color = 0x4ccafc;
  
  coverImage = show["coverImage"];
  id = show["id"];
  status = show["status"];
  volumes = volumesCheck(show["volumes"]);
  chapters = chaptersCheck(show["chapters"]);
  footerText = f"Volumes: {volumes}  Chapters: {chapters}"
  
  await updateUserList(id, progress=chapter, discordUserId=discordUserId)
  if chend:
    await asyncio.sleep(0.1)
    await updateUserList(id, progress=chend, discordUserId=discordUserId)
  if volume:
    await asyncio.sleep(0.1)
    await updateUserList(id, progressVolumes=volume, discordUserId=discordUserId)
    if vend:
      await asyncio.sleep(0.1)
      await updateUserList(id, progressVolumes=vend, discordUserId=discordUserId)

  embed = embedCreator(title=title, description=description, color=color, imageUrl=coverImage, footerText=footerText);
  return { "embed": embed, "status": status }

async def userReadEmbed(show, chapter, chend, volume, vend, discordUserId):
  userData = getUserDetails(discordUserId);

  if userData:
      anilistUsername = userData["anilistUsername"];

  title = show["title"];

  if chend and volume and vend:
    description = f"{anilistUsername} Read **Ch.{chapter}-Ch.{chend}** and **Vol.{volume}-Vol.{vend}** of **{title}**";
  elif chend and volume:
    description = f"{anilistUsername} Read **Ch.{chapter}-Ch.{chend}** and **Vol.{volume}** of **{title}**";
  elif chend:
    description = f"{anilistUsername} Read **Ch.{chapter}-Ch.{chend}** of **{title}**";
  elif volume and vend:
    description = f"{anilistUsername} Read **Ch.{chapter}** and **Vol.{volume}-Vol.{vend}** of **{title}**";
  elif volume:
    description = f"{anilistUsername} Read **Ch.{chapter}** and **Vol.{volume}** of **{title}**";
  else:
    description = f"{anilistUsername} Read **Ch.{chapter}** of **{title}**";
  
  color = 0x7542f5;
  
  coverImage = show["coverImage"];
  volumes = volumesCheck(show["volumes"]);
  chapters = chaptersCheck(show["chapters"]);
  footerText = f"Volumes: {volumes}  Chapters: {chapters}"

  embed = embedCreator(title=title, description=description, color=color, imageUrl=coverImage, footerText=footerText);
  return embed

async def getUserMangaList(discordUserId):
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
              progressVolumes
            }
            status
          }
        }
      }""";
  
      variables =  {
        "userName": anilistUsername,
        "type": "MANGA",
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
            progressVolumes = entry["progressVolumes"];
            
            data = {
              "title": title,
              "id": id,
              "progress": progress,
              "progressVolumes": progressVolumes,
              "status": status
            };

            results.append(data);

    return results
    
  except:
    print("There was a problem with the getUserMangaList function")

async def read_command(interaction: discord.Interaction, title, format, chapter, chend, volume, vend):
  discordUserId = str(interaction.user.id);
  mangaList = await getUserMangaList(discordUserId);
  manga = await searchShowByTitle(title, "MANGA", format, interaction, True);
  # print(anime);

  if not manga:
    return
  
  mangaTitle = manga["title"];
  mangaId = manga["id"];
  # checkResult = checkIfShowIsCurrent(mangaList, manga);

  fixResults = fixShowInfo(mangaList, manga, chapter, chend, volume, vend, mangaTitle);
  # print(fixResults)

  if fixResults and fixResults["status"] != "Alright":
    res = fixResults["response"];
    await interaction.followup.send(res);
    return
  
  if chend and chend == chapter:
    chend = None;
  if vend and vend == volume:
    vend = None;

  reResult = await readEmbed(manga, chapter, chend, volume, vend, discordUserId);
  embed = reResult["embed"];
  status = reResult["status"];

  await interaction.followup.send(embeds=[embed]);

  if status == "RELEASING":
    if discordUserId == "317725955080847361":
      results = await checkUsersList("Salbtw", mangaId);
      if results["found"] and results["status"] == "CURRENT":
        progress = results["progress"]
        isProgressEqual = checkProgressEqual(progress, chapter, chend)
        if isProgressEqual:
          channel = await interaction.guild.fetch_channel(1180588268576849980);
          embed = await userReadEmbed(manga, chapter, chend, volume, vend, discordUserId);
          await channel.send(embeds=[embed])

    if discordUserId == "373499146507649034":
      results = await checkUsersList("XNA", mangaId);
      if results["found"] and results["status"] == "CURRENT":
        progress = results["progress"]
        isProgressEqual = checkProgressEqual(progress, chapter, chend)
        if isProgressEqual:
          channel = await interaction.guild.fetch_channel(1180588268576849980);
          embed = await userReadEmbed(manga, chapter, chend, volume, vend, discordUserId);
          await channel.send(embeds=[embed])

