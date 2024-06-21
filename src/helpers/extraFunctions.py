import re;
import camelcase;

c = camelcase.CamelCase();

def stripHtmlTags(html):
  return re.sub(r"<[^>]+>", "", html)

def capitalizeFirstLetter(word):
  if type(word) == str:
    smallWord = word.lower()

    final = c.hump(smallWord)

  return final;

def episodesCheck(episodes):
  if not episodes:
    episodes = "Ongoing";
    return episodes
  else:
    episodes = str(episodes);
    return episodes
  
def volumesCheck(volumes):
  if not volumes:
    volumes = "Ongoing";
    return volumes
  else:
    volumes = str(volumes);
    return volumes
  
def chaptersCheck(chapters):
  if not chapters:
    chapters = "Ongoing";
    return chapters
  else:
    chapters = str(chapters);
    return chapters