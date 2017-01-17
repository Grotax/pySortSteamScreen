#!/usr/bin/env python3
import requests
import os
import json

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
            data = r.text
            data = json.loads(data)
            if (data[steamID]['success']):
                knownNames[steamID] = data[steamID]['data']['name']
                return knownNames.get(steamID)
            else:
                return steamID
        else:
            return steamID


def moveFiles(steamID, name):
    for ch in ['/','\\',':','*','?','"','<','>','|']:
        if ch in name:
            name=name.replace(ch,"")
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


def main():
    global knownNames
    try:
        with open("knownNames.json", "r") as f:
            knownNames = json.load(f)
    except FileNotFoundError as e:
        knownNames = {}

    for file in os.listdir(os.getcwd()):
        name = os.path.basename(file)
        split = name.partition("_")
        if not os.path.isdir(file) and not split[1] == "":
            steamID = split[0]
            print(getSteamName(steamID))
            moveFiles(steamID, getSteamName(steamID))

    with open("knownNames.json", "w") as f:
        json.dump(knownNames, f)

if __name__ == '__main__':
    main()
