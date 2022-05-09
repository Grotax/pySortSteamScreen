#!/usr/bin/env python3
"""Move steam screenshots from collection"""

import os
import re
import sys
import json
import argparse

import requests

__version__ = "0.1"

JSON_FILENAME = "knownNames.json"


def get_arguments():
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pattern", default=r"(\d+)_\d+.*", metavar="REGEX",
             dest="pattern", help="Use a custom pattern to find "+
             "Identifier to use Program for other purposes. "+
             "The first Group found will be used as Identifier")
    parser.add_argument("--offline", action="store_false", dest="connect",
             default=True, help="Do not attempt got get Name for Steam ID")
    parser.add_argument("-q", action="store_true", dest="quiet",
             default=False, help="Don't print file movement notifications.")
    parser.add_argument("-j", "--json", action="store_true", dest="json",
             default=False,
             help="Don't move anything, just generate JSON File. "+
             "Useful to Rename unknown Names before Generating Folders")
    return parser.parse_args()


def get_steam_name(steam_id, known_names):
    """Translate a steam id into the name of a game."""
    if steam_id in known_names:
        return known_names[steam_id]['name']
    else:
        # Steam id max
        if 0 < int(steam_id) < 9223372036854775807:
            payload = {'appids': steam_id}
            req = requests.get('https://store.steampowered.com/api/appdetails/', params=payload)
            data = req.json()
            if data[steam_id]['success']:
                entry = {}
                entry['name'] = data[steam_id]['data']['name']
                entry['steam'] = True
                known_names[steam_id] = entry
                return known_names[steam_id]['name']
            else:
                # if we can't get a name from Steam we set the id as name
                entry = {}
                entry['name'] = steam_id
                # if True name is in Steam Shop, else False
                entry['steam'] = False
                known_names[steam_id] = entry
                return known_names[steam_id]['name']
        else:
            entry = {}
            entry['name'] = steam_id
            entry['steam'] = False
            known_names[steam_id] = entry
            return known_names[steam_id]['name']


def make_safe_filename(name):
    """Replace characters that are not allowed in windows file names."""
    for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:  # Windows illegal folder chars
        if char in name:
            name = name.replace(char, " ")
            # replacables:  ['∕','⧵' ,'˸','⁎','ॽ','“','ᑄ','ᑀ','┃']  #similar chars
    return name


def move_files(steam_id, name, arguments):
    """Move all screenshots of a specific game into the corresponding folder."""
    name = make_safe_filename(name)
    newdir = os.getcwd()+"/"+name
    if not os.path.exists(newdir):
        os.makedirs(newdir)
        print(newdir + " was created.")
    for file in os.listdir(os.getcwd()):
        name = os.path.basename(file)
        pat = re.search(r"(.*)\(.*\)(.*)", arguments.pattern)
        reregex = pat.group(1) + steam_id + pat.group(2)
        if not os.path.isdir(file) and re.search(reregex,name):
            newname = newdir + "/" + os.path.basename(file)
            if not arguments.quiet:
                print("{} --> {}".format(file, newname))
            os.rename(file, newname)


def load_json():
    """Load the translation dictionary."""
    try:
        with open(JSON_FILENAME, "r", encoding="utf8") as file:
            known_names = json.load(file)
            if "version" in known_names:
                if known_names.get("version") < __version__:
                    print("Unkown version: {}, current version: {}".format(
                        known_names.get("version"), __version__))
                    known_names = {}
            else:
                print("No version number found")
                known_names = {}
    except FileNotFoundError:
        known_names = {}
    return known_names


def write_json(known_names):
    """Update the translation dictionary."""
    with open(JSON_FILENAME, "w", encoding="utf8") as file:
        known_names.update({"version": __version__})
        json.dump(known_names, file, indent="\t")


def main():
    """Sort steam screenshots into a folder structure."""
    arguments = get_arguments()
    id_set = set()
    known_names = load_json()
    for file in os.listdir(os.getcwd()):
        name = os.path.basename(file)
        regex = arguments.pattern
        search = re.search(regex, name)
        if (not os.path.isdir(file)
                and not name == sys.argv[0]
                and not name == JSON_FILENAME):
            try:
                steam_id = search.group(1)
                id_set.add(steam_id)
            except IndexError: #Regex did not find group
                continue
            except AttributeError: #Regex did not match
                continue
    print(id_set)
    for steam_id in id_set:
        if arguments.connect:
            steam_name = get_steam_name(steam_id, known_names)
        else:
            steam_name = steam_id
        if not arguments.json:
            print("Game Name:", steam_name)
            move_files(steam_id, steam_name, arguments)
    write_json(known_names)


if __name__ == '__main__':
    main()
