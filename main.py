#!/usr/bin/env python3
import requests

knownNames = {}


def getName(SteamID):
    global knownNames
    if(SteamID in knownNames):
        return knownNames.get(SteamID)
    else:
        payload = {'appids': SteamID}
        r = requests.get('https://store.steampowered.com/api/appdetails/', params=payload)
        data = r.json()
        knownNames[SteamID] = data[SteamID]['data']['name']
        return knownNames.get(SteamID)


def main():
    print(getName('440'))
    print(getName('250900'))

if __name__ == '__main__':
    main()
