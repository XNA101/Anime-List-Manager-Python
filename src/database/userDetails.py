from db import *;

def getUserDetails(discordUserId):
  userRef = db.collection("userInformation").document(discordUserId);
  userSnapshot = userRef.get();
  userData = userSnapshot._data;

  if userData:

    accessToken = userData["anilistAccessToken"];
    anilistUsername = userData["anilistUsername"];

    userObj = {
      "accessToken": accessToken,
      "anilistUsername": anilistUsername
    }

    return userObj;

  else:
    
    errObj = {
      "Error": "Missing information! user might not be authenticated"
    }

    return errObj;