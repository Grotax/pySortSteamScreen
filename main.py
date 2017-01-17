#!/usr/bin/env python3
import requests
import os

knownNames = {}


def getSteamName(steamID):
    global knownNames
    if(steamID in knownNames):
        return knownNames.get(steamID)
    else:
        # Steam id max
        if int(steamID) < 9223372036854775807:
            payload = {'appids': steamID}
            r = requests.get('https://store.steampowered.com/api/appdetails/', params=payload)
            data = r.json()
            print(data[steamID]['success'])
            knownNames[steamID] = data[steamID]['data']['name']
            return knownNames.get(steamID)
        else:
            print("Not a Steam game.")
            return "Unkown"


def moveFiles(steamID, name):
    newdir = os.getcwd()+"/"+name
    if not os.path.exists(newdir):
        os.makedirs(newdir)
        print(newdir+" was created.")
    for file in os.listdir(os.getcwd()):
        name = os.path.basename(file)
        if name.startswith(steamID):
            newname = newdir+"/"+os.path.basename(file)
            print("%s --> %s" % (file, newname))
            os.rename(file, newname)


def main():
    for file in os.listdir(os.getcwd()):
        name = os.path.basename(file)
        split = name.partition("_")
        if not split[1] == "":
            steamID = name.partition("_")[0]
            print(getSteamName(steamID))
            moveFiles(steamID, getSteamName(steamID))

if __name__ == '__main__':
    main()
