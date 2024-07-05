import discord;
from db import *;
import requests;
from helpers.buttons import *;
from helpers.embedCreator import *;
from database.userDetails import *;
from helpers.extraFunctions import *;

Embed = discord.Embed;

def createDescription(show, score, status):
  title = show["title"];
  progress = show["progress"];
  if status == "Completed":
    description = f"Score: {score}/10\nStatus: {status}"
    return description
  else:
    if progress == None or progress ==  0:
      description = f"You haven't read any chapters of **{title}**\nStatus: {status}"
      return description
    else:
      description = f"Last Read: **Ch.{progress}**\nStatus: {status}"
      return description

def createFooterText(anilistUsername, currentIndex, totalManga):
  footerText = f"{anilistUsername}'s list | Page {currentIndex + 1}/{totalManga}";
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
  totalManga = self.format["totalManga"];
  footerText = self.createFooterText(anilistUsername, currentIndex, totalManga);
  footerUrl = self.format["footerUrl"];

  embed = embedCreator(title=title, description=description, color=color, imageUrl=imageUrl, footerText=footerText, footerUrl=footerUrl);
  return embed

def createEmbed(mangaList, page = None):
  if page:
    manga = mangaList[page];
    index = page;
    title = manga["title"];
    coverImage = manga["coverImage"];
    score = manga["score"];
    status = manga["status"];
    anilistUsername = manga["anilistUsername"];
    userAvatar = manga["userAvatar"];
  
    currentIndex = index;
    totalManga = len(mangaList);
  
    description = createDescription(manga, score, status);
    color = embedColor(status);
    imageUrl = coverImage;
    footerText = f"{anilistUsername}'s list | Page {currentIndex + 1}/{totalManga}";
    footerUrl = userAvatar;

    Format = { "color": color, "footerUrl": footerUrl, "totalManga": totalManga };

    embed = embedCreator(title=title, description=description, color=color, imageUrl=imageUrl, footerText=footerText, footerUrl=footerUrl);
    return { "embed": embed, "index": index, "format": Format }

  if not page:
    for manga in mangaList:
      index = mangaList.index(manga);
      title = manga["title"];
      coverImage = manga["coverImage"];
      score = manga["score"];
      status = manga["status"];
      anilistUsername = manga["anilistUsername"];
      userAvatar = manga["userAvatar"];

      currentIndex = index;
      totalManga = len(mangaList);

      description = createDescription(manga, score, status);
      color = embedColor(status);
      imageUrl = coverImage;
      footerText = f"{anilistUsername}'s list | Page {currentIndex + 1}/{totalManga}";
      footerUrl = userAvatar;

      Format = { "color": color, "footerUrl": footerUrl, "totalManga": totalManga };

      embed = embedCreator(title=title, description=description, color=color, imageUrl=imageUrl, footerText=footerText, footerUrl=footerUrl);
      return { "embed": embed, "index": index, "format": Format }

async def getUserMangaList(discordUserId, status):
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
        "type": "MANGA",
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
    print("There was a problem with the getUserMangaList function")

async def mangalist_command(interaction: discord.Interaction, status: str, page: int):
  discordUserId = str(interaction.user.id);
  mangaList = await getUserMangaList(discordUserId, status);
  if page:
    if page > len(mangaList):
      status = mangaList[0]["status"]
      await interaction.followup.send(f"Your **{status}** manga list has only **{len(mangaList)}** pages. You've tried to go to page {page}");
      return
    if page < -len(mangaList):
      await interaction.followup.send(f"Your **{status}** manga list has only **{len(mangaList)}** pages. You've tried to go to page {page}");
      return
    if page < 0:
      page = (len(mangaList) + page) - 1
    else:
      page = page - 1
  if not page:
    page = 0
  
  if type(mangaList) == None:
    await interaction.followup.send("User information not found.");
    return
  
  if len(mangaList) == 0:
    await interaction.followup.send(f"Your **{capitalizeFirstLetter(status)}** list is empty.");
    return
  
  if page:
    embed = createEmbed(mangaList, page)["embed"];
    currentIndex = createEmbed(mangaList, page)["index"];
    Format = createEmbed(mangaList, page)["format"];
  if not page:
    embed = createEmbed(mangaList)["embed"];
    currentIndex = createEmbed(mangaList)["index"];
    Format = createEmbed(mangaList)["format"];
  
  mangaListFormat = { "list": mangaList,  "format": Format};

  # interaction.response.send_message(embeds=embed, view=create_button(mangaList, currentIndex))
  btn = create_button(mangaListFormat, currentIndex, embed, createDescription, getCurrentEmbed, createFooterText )
  await interaction.followup.send(embeds=[embed], view=btn)
  # print(val);