import re;
from google.cloud import firestore;
from db import *;

def fixName(name):
  return re.sub(r"[^a-zA-Z0-9]", "_", name);

def getServerDetails(serverName, serverId):
  collRef = db.collection("servers");
  docRef = collRef.document(serverId).collection(serverName).document("registeredChannels");
  docSnapshot = docRef.get();
  data = docSnapshot._data;

  return { "data": data, "docRef": docRef }
    
def addServerDetail(serverName, channelId, serverId, channelName):
  data = getServerDetails(serverName, serverId)["data"];
  docRef = getServerDetails(serverName, serverId)["docRef"];

  status = "Not Done";
  channelName = fixName(channelName);
  
  if data == {}:
    docRef.set({ f"{channelName}": channelId });
    status = "Done";
    return status;

  if data:
    if channelName in data:
      chnlId = data[channelName]
      if str(chnlId) == channelId:
          # print(data);
          status = "Already registered";
          return status
    else:
      docRef.update({ f"{channelName}": channelId })
      status = "Done";
      return status
    
def delServerDetail(serverName, serverId, channelName):
  data = getServerDetails(serverName, serverId)["data"];
  docRef = getServerDetails(serverName, serverId)["docRef"];

  status = "Not Done";
  channelName = fixName(channelName);
  
  if data == {}:
    status = "No Channels are registered";
    return status;

  if data:
    if channelName in data:
      docRef.update({ f"{channelName}": firestore.DELETE_FIELD });
      status = "Done";
      return status;
    else:
      status = "Channel is not registered";
      return status

def isRegistered(interaction):
  serverName = interaction.guild.name;
  serverId = str(interaction.guild.id);
  channelId = str(interaction.channel.id)

  data = getServerDetails(serverName, serverId)["data"];

  registered = False;

  if data:
    for chName in data:
      chId = data[chName];
      if chId == channelId:
        registered = True

  return registered;
