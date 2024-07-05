import discord;
from db import *;
import requests;
from helpers.buttons import *;
from helpers.embedCreator import *;
from database.userDetails import *;
from helpers.extraFunctions import *;

def createDescription(show, score, status):
  title = show["title"];
  progress = show["progress"];
  if status == "Completed":
    description = f"Score: {score}/10\nStatus: {status}"
    return description
  else:
    if progress == None or progress ==  0:
      description = f"You haven't watched any episodes of **{title}**\nStatus: {status}"
      return description
    else:
      description = f"Last Watched: **Ep.{progress}**\nStatus: {status}"
      return description

def createFooterText(anilistUsername, currentIndex, totalAnime):
  footerText = f"{anilistUsername}'s list | Page {currentIndex + 1}/{totalAnime}";
  return footerText

def embedColor(status):
  if status == "Current":
    return 0x4ccafc
  if status == "Completed":
    return 0x16fa44
  if status == "Planning":
    return 0xdf4cfc
  if status == "Dropped":
    return 0xff5542
  if status == "Repeating":
    return 0x42f587
  else:
    return 0xffffff

def getCurrentEmbed(self):
  newList = self.List[self.currentIndex];
  title = newList["title"];
  score = newList["score"];
  status = newList["status"];
  description = self.createDescription(newList, score, status);
  color = self.format["color"];
  imageUrl = newList["coverImage"];
  anilistUsername = newList["anilistUsername"];
  currentIndex = self.currentIndex;
  totalAnime = self.format["totalAnime"];
  footerText = self.createFooterText(anilistUsername, currentIndex, totalAnime);
  footerUrl = self.format["footerUrl"];

  embed = embedCreator(title=title , description=description, color=color, imageUrl=imageUrl, footerText=footerText, footerUrl=footerUrl);
  return embed

def createEmbed(animeList, page = None):
  if page:
    anime = animeList[page];
    index = page;
    title = anime["title"];
    coverImage = anime["coverImage"];
    score = anime["score"];
    status = anime["status"];
    anilistUsername = anime["anilistUsername"];
    userAvatar = anime["userAvatar"];
  
    currentIndex = index;
    totalAnime = len(animeList);
  
    description = createDescription(anime, score, status);
    color = embedColor(status);
    imageUrl = coverImage;
    footerText = f"{anilistUsername}'s list | Page {currentIndex + 1}/{totalAnime}";
    footerUrl = userAvatar;

    Format = { "color": color, "footerUrl": footerUrl, "totalAnime": totalAnime };

    embed = embedCreator(title=title, description=description, color=color, imageUrl=imageUrl, footerText=footerText, footerUrl=footerUrl);
    return { "embed": embed, "index": index, "format": Format }

  if not page:
    for anime in animeList:
      index = animeList.index(anime);
      title = anime["title"];
      coverImage = anime["coverImage"];
      score = anime["score"];
      status = anime["status"];
      anilistUsername = anime["anilistUsername"];
      userAvatar = anime["userAvatar"];

      currentIndex = index;
      totalAnime = len(animeList);

      description = createDescription(anime, score, status);
      color = embedColor(status);
      imageUrl = coverImage;
      footerText = f"{anilistUsername}'s list | Page {currentIndex + 1}/{totalAnime}";
      footerUrl = userAvatar;

      Format = { "color": color, "footerUrl": footerUrl, "totalAnime": totalAnime };

      embed = embedCreator(title=title, description=description, color=color, imageUrl=imageUrl, footerText=footerText, footerUrl=footerUrl);
      return { "embed": embed, "index": index, "format": Format }

async def getUserAnimeList(discordUserId, status):
  try:
    userData = getUserDetails(discordUserId);
  
    if userData:
      accessToken = userData["accessToken"];
      anilistUsername = userData["anilistUsername"];
      
      query = """
      query ($userName: String, $type: MediaType, $sort: [MediaListSort], $status: MediaListStatus) { # Define which variables will be used in the query (id)
        MediaListCollection (userName: $userName, type: $type, sort: $sort, status: $status) {
          user {
            avatar {
              large
            }
          }
          lists {
            entries {
              media {
                title {
                  userPreferred
                }
                coverImage{
                  large
                }
              }
              score
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
        "status": status,
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

        userAvatar = data["data"]["MediaListCollection"]["user"]["avatar"]["large"];
        lists = data["data"]["MediaListCollection"]["lists"]
        results = []
        for List in lists:
          status = capitalizeFirstLetter(status);
          entries = List["entries"];
          for entry in entries:
            title = entry["media"]["title"]["userPreferred"];
            coverImage = entry["media"]["coverImage"]["large"];
            score = entry["score"];
            progress = entry["progress"];
            
            data = {
              "title": title,
              "coverImage": coverImage,
              "score": score,
              "status": status,
              "progress": progress,
              "anilistUsername": anilistUsername,
              "userAvatar": userAvatar
            };

            results.append(data);

    return results
    
  except:
    print("There was a problem with the getUserAnimeList function")

async def animelist_command(interaction: discord.Interaction, status: str, page: int):
  discordUserId = str(interaction.user.id);
  animeList = await getUserAnimeList(discordUserId, status);
  if page:
    if page > len(animeList):
      status = animeList[0]["status"]
      await interaction.followup.send(f"Your **{status}** anime list has only **{len(animeList)}** pages. You've tried to go to page {page}");
      return
    if page < -len(animeList):
      await interaction.followup.send(f"Your **{status}** anime list has only **{len(animeList)}** pages. You've tried to go to page {page}");
      return
    if page < 0:
      page = (len(animeList) + page) - 1
    else:
      page = page - 1
  if not page:
    page = 0
  
  if animeList == None:
    await interaction.followup.send("User information not found.");
    return
  
  if len(animeList) == 0:
    await interaction.followup.send(f"Your **{capitalizeFirstLetter(status)}** list is empty.");
    return
  
  if page:
    embed = createEmbed(animeList, page)["embed"];
    currentIndex = createEmbed(animeList, page)["index"];
    Format = createEmbed(animeList, page)["format"];
  if not page:
    embed = createEmbed(animeList)["embed"];
    currentIndex = createEmbed(animeList)["index"];
    Format = createEmbed(animeList)["format"];
  
  animeListFormat = { "list": animeList,  "format": Format};

  # interaction.response.send_message(embeds=embed, view=create_button(animeList, currentIndex))
  btn = create_button(animeListFormat, currentIndex, embed, createDescription, getCurrentEmbed, createFooterText )
  await interaction.followup.send(embeds=[embed], view=btn)
  # print(val);