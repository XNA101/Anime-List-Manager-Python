import re;
import time;
from google.cloud import firestore;
from db import *;

def fixTitle(title):
  return re.sub(r"[^a-zA-Z0-9]", "_", title);

def sortTimeStampList(data):
  timeStampsArray = []
  for _, showIdWithTime in data.items():
    showIdWithTime: str
    _, timeStap = showIdWithTime.split(":")
    timeStampsArray.append(int(timeStap))
  orderTimeStamps = sorted(timeStampsArray)
  return orderTimeStamps

def sortRecDetailsList(data):
  orderedObj = {}
  sortedTimeStampsArray = sortTimeStampList(data)
  for title, showIdWithTime in data.items():
    showIdWithTime: str
    showid, timestamp = showIdWithTime.split(":")
    showId = int(showid)
    timeStamp = int(timestamp)
    orderedObj[timeStamp] = (title, showId)

  sortedData = {}

  for timestamp in sortedTimeStampsArray:
    sortedData[orderedObj[timestamp][0]]  = orderedObj[timestamp][1]
    
  # sortedData = {orderedObj[timestamp][0]: orderedObj[timestamp][1] for timestamp in sortedTimeStampsArray}
  # print(sortedData)
  # print(sortedTimeStampsArray)
  # print(sortedData);
  return sortedData;
    
async def recDetails(userName, type, genre):
  recRef = db.collection("recommendations").document(userName).collection(type).document(genre);
  snapshot = recRef.get();
  # print(dir(snapshot._to_protobuf().fields.get()))
  data = snapshot._data;
  sortedData = sortRecDetailsList(data)
  return sortedData; 

async def fullRecDetails(userName, type):
  type = type.capitalize()
  recRef = db.collection("recommendations").document(userName).collection(type)
  recSnapshot = recRef.get();

  recInfo = [];
  showsArray = [];

  for doc in recSnapshot:
    recInfo.append({ "id": doc.id, "data": doc._data });

  for show in recInfo:
    genre = show["id"];
    data = show["data"];
    if len(data) != 0:
      sortedData = sortRecDetailsList(data);
      for title, showId in sortedData.items():
        showsArray.append({ "genre": genre, "title": title, "showId": showId });
  
  return showsArray;

async def addRec(userName, type, genre, title, showId):
  title = fixTitle(title);
  recRef = db.collection("recommendations").document(userName).collection(type).document(genre);
  docId = int(time.time())
  recRef.update({ f"{title}": f"{showId}:{docId}" });

async def delRec(userName, type, genre, title):
  recRef = db.collection("recommendations").document(userName).collection(type).document(genre);
  snapshot = recRef.get();
  data = snapshot._data;

  title = fixTitle(title);

  showInRec = False;

  for rec in data:
    if rec == title:
      showInRec = True;

  if showInRec:
    recRef.update({ f"{title}": firestore.DELETE_FIELD});

  if not showInRec:
    return showInRec;