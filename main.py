#!/usr/bin/env python3
import requests
import os
import json

knownNames = {}
version = "0.1"


def getSteamName(steamID):
    global knownNames
    if(steamID in knownNames):
        return knownNames.get(steamID)
    else:
        # Steam id max
        intSteamID = int(steamID)
        if intSteamID > 0 and intSteamID < 9223372036854775807:
            payload = {'appids': steamID}
            r = requests.get('https://store.steampowered.com/api/appdetails/', params=payload)
            data = r.json()
            if (data[steamID]['success']):
                knownNames[steamID]['name'] = data[steamID]['data']['name']
                knownNames[steamID]['steam'] = True
                return knownNames.get(steamID)
            else:
                # if we can't get a name from Steam we set the id as name
                knownNames[steamID]['name'] = steamID
                # if True name is in Steam Shop, else False
                knownNames[steamID]['steam'] = False
                return steamID
        else:
            knownNames[steamID]['name'] = steamID
            knownNames[steamID]['steam'] = False
            return steamID


def fileName(name):
    for ch in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:  # Windows illegal folder chars
        if ch in name:
            name = name.replace(ch, "")
            # replacables:  ['∕','⧵' ,'˸','⁎','ॽ','“','ᑄ','ᑀ','┃']  #similar chars
    return name


def moveFiles(steamID, name):
    name = fileName(name)
    newdir = os.getcwd()+"/"+name
    if not os.path.exists(newdir):
        os.makedirs(newdir)
        print(newdir+" was created.")
    for file in os.listdir(os.getcwd()):
        name = os.path.basename(file)
        if not os.path.isdir(file) and name.startswith(steamID):
            newname = newdir+"/"+os.path.basename(file)
            print("%s --> %s" % (file, newname))
            os.rename(file, newname)


def loadJson():
    global knownNames
    try:
        with open("knownNames.json", "r") as f:
            knownNames = json.load(f)
            if "version" in knownNames:
                if knownNames.get("version") != version:
                    print("Unkown version: %s, current version: %s" % (knownNames.get("version"), version))
                    knownNames = {}
            else:
                print("No version number found")
                knownNames = {}
    except FileNotFoundError as e:
        knownNames = {}


def writeJson():
    global knownNames
    with open("knownNames.json", "a") as f:
        knownNames.update({"version": version})
        json.dump(knownNames, f, indent="\t")


def main():
    global knownNames
    idList = {}

    loadJson()

    for file in os.listdir(os.getcwd()):
        name = os.path.basename(file)
        split = name.partition("_")
        if not os.path.isdir(file) and not split[1] == "":
            steamID = split[0]
            idList.update(steamID)
        for steamID in idList:
            steamName = getSteamName(steamID)
            print("Game Name: %s" % steamName)
            moveFiles(steamID, steamName)
        writeJson()

if __name__ == '__main__':
    main()
