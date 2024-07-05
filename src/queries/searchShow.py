import discord;
import requests;
from helpers.extraFunctions import *;

async def searchShowByTitle(show, type, format, interaction: discord.Interaction, defer = None):
  query = """
    query ($search: String, $type: MediaType, $format: MediaFormat) {
        Media (search: $search, type: $type, format: $format) {
          title {
            userPreferred
          }
          description
          volumes
          chapters
          episodes
          coverImage {
            large
          }
          id
          status
          nextAiringEpisode {
            episode
          }
        }
      }
    """;
  if format == "None":
    variables = {
      "search": show,
      "type": type,
    }
  else:
    variables = {
      "search": show,
      "type": type,
      "format": format
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
    data = res.json()["data"];
    title = data["Media"]["title"]["userPreferred"];

    if data["Media"]["description"]:
      description = stripHtmlTags(data["Media"]["description"]);
    else:
      description = None

    episodes = data["Media"]["episodes"];
    coverImage = data["Media"]["coverImage"]["large"];
    id = data["Media"]["id"];
    status = data["Media"]["status"];
    if status == "RELEASING" and type == "ANIME":
      nextEpisode = data["Media"]["nextAiringEpisode"]["episode"];
    volumes = data["Media"]["volumes"];
    chapters = data["Media"]["chapters"];

    if status == "RELEASING" and type == "ANIME":
      results = {
        "title": title,
        "description": description,
        "episodes": episodes,
        "coverImage": coverImage,
        "id": id,
        "status": status,
        "nextEpisode": nextEpisode,
        "volumes": volumes,
        "chapters": chapters
      }
    else:
      results = {
        "title": title,
        "description": description,
        "episodes": episodes,
        "coverImage": coverImage,
        "id": id,
        "status": status,
        "volumes": volumes,
        "chapters": chapters
      }

    return results
  
  if res.status_code == 404:
    if defer == None:
      await interaction.response.send_message("Please make sure to input the right values for the fields.");
    if defer == True:
      await interaction.followup.send("Please make sure to input the right values for the fields.");
      
async def searchShowById(showId, type):
  query = """
    query ($id: Int, $type: MediaType) {
        Media (id: $id, type: $type) {
        title {
          userPreferred
        }
        episodes
        chapters
        volumes
        type
        coverImage {
          large
        }
        format
        id
      } 
    }
  """;

  variables = {
    "id": showId,
    "type": type,
  };

  Headers = {
      "Content-Type": "application/json",
      "Accept": "application/json",
    }

  Json = {
      "query": query,
      "variables": variables,
    };

  res = requests.post(url="https://graphql.anilist.co", headers=Headers, json=Json);

  if res.status_code == 200:
    data = res.json()

    media = data["data"]["Media"];

    title = media["title"]["userPreferred"];
    episodes = media["episodes"];
    chapters = media["chapters"];
    volumes = media["volumes"];
    coverImage = media["coverImage"]["large"];
    format = media["format"];
    id = media["id"];
    type = media["type"]

    resultObj = {
      "title": title,
      "episodes": episodes,
      "chapters": chapters,
      "volumes": volumes,
      "coverImage": coverImage,
      "format": format,
      "id": id,
      "type": type
    }

    return resultObj;    