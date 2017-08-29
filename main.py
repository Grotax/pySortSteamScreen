#!/usr/bin/env python3
import requests
import os
import json
import sys
import re
from optparse import OptionParser

knownNames = {}
version = "0.1"


def getArguments():
    parser = OptionParser()
    parser.add_option("-p", "--pattern", default="(\d+)_\d+.*", metavar="REGEX",
             dest="pattern", help="Use a custom pattern to find "+
             "Identifier to use Program for other purposes. "+
             "The first Group found will be used as Identifier")
    parser.add_option("--offline", action="store_false", dest="Connect",
             default=True, help="Do not attempt got get Name for Steam ID")
    parser.add_option("-q", action="store_true", dest="quiet",
             default=False, help="Don't print file movement notifications.")
    parser.add_option("-j", "--json", action="store_true", dest="json",
             default=False,
             help="Don't move anything, just generate JSON File. "+
             "Useful to Rename unknown Names before Generating Folders")
    return parser.parse_args()


def getSteamName(steamID):
    global knownNames
    if(steamID in knownNames):
        return knownNames[steamID]['name']
    else:
        # Steam id max
        intSteamID = int(steamID)
        if intSteamID > 0 and intSteamID < 9223372036854775807:
            payload = {'appids': steamID}
            r = requests.get('https://store.steampowered.com/api/appdetails/', params=payload)
            data = r.json()
            if (data[steamID]['success']):
                entry = {}
                entry['name'] = data[steamID]['data']['name']
                entry['steam'] = True
                knownNames[steamID] = entry
                return knownNames[steamID]['name']
            else:
                # if we can't get a name from Steam we set the id as name
                entry = {}
                entry['name'] = steamID
                # if True name is in Steam Shop, else False
                entry['steam'] = False
                knownNames[steamID] = entry
                return knownNames[steamID]['name']
        else:
            entry = {}
            entry['name'] = steamID
            entry['steam'] = False
            knownNames[steamID] = entry
            return knownNames[steamID]['name']


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
        pat = re.search("(.*)\(.*\)(.*)",options.pattern)
        reregex = pat.group(1) + steamID + pat.group(2)
        if not os.path.isdir(file) and re.search(reregex,name):
            newname = newdir+"/"+os.path.basename(file)
            if not options.quiet: print("%s --> %s" % (file, newname))
            os.rename(file, newname)


def loadJson():
    global knownNames
    try:
        with open("knownNames.json", "r") as f:
            knownNames = json.load(f)
            if "version" in knownNames:
                if float(knownNames.get("version")) < version:
                    print("Unkown version: %s, current version: %s" % (knownNames.get("version"), version))
                    knownNames = {}
            else:
                print("No version number found")
                knownNames = {}
    except FileNotFoundError as e:
        knownNames = {}


def writeJson():
    global knownNames
    jsonFile = open("knownNames.json", "w")
    jsonFile.close()
    with open("knownNames.json", "a") as f:
        knownNames.update({"version": version})
        json.dump(knownNames, f, indent="\t")


def main():
    global options, args
    options, args = getArguments()
    global knownNames
    idSet = set()
    loadJson()
    for file in os.listdir(os.getcwd()):
        name = os.path.basename(file)
        Regex = options.pattern
        Search = re.search(Regex, name)
        if not os.path.isdir(file) and \
        not name == sys.argv[0] and \
        not name == "knownNames.json":
            try:
                steamID = Search.group(1)
                idSet.add(steamID)
            except IndexError: #Regex did not find group
                continue
            except AttributeError: #Regex did not match
                continue
    print(idSet)
    for steamID in idSet:
        if options.Connect:
            steamName = getSteamName(steamID)
        else:
            steamName = steamID
        if not options.json:
            print("Game Name: %s" % steamName)
            moveFiles(steamID, steamName)
    writeJson()

if __name__ == '__main__':
    main()
