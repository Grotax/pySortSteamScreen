#!/usr/bin/env python3
"""Move steam screenshots from collection"""

import re
import json
import shutil
import pathlib
import argparse

import requests

__version__ = "0.1.0"
__license__ = "MIT"

JSON_VERSION = "0.1"
JSON_FILENAME = "knownNames.json"


def get_arguments():
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_false", dest="connect",
                        default=True, help="Do not attempt got get Name for Steam ID")
    parser.add_argument("-q", action="store_true", dest="quiet",
                        default=False, help="Don't print file movement notifications.")
    parser.add_argument("-j", "--json", action="store_true", dest="json",
                        default=False,
                        help="Don't move anything, just generate JSON File. " +
                        "Useful to Rename unknown Names before Generating Folders")
    return parser.parse_args()


def get_steam_name(steam_id, known_names):
    """Translate a steam id into the name of a game."""
    if steam_id in known_names:
        return known_names[steam_id]['name']
    else:
        entry = {}
        if 0 < int(steam_id) < 9223372036854775807:
            payload = {'appids': steam_id}
            req = requests.get(
                'https://store.steampowered.com/api/appdetails/', params=payload)
            data = req.json()
            if data[steam_id]['success']:
                entry['name'] = data[steam_id]['data']['name']
                entry['steam'] = True
            else:
                # if we can't get a name from Steam we set the id as name
                entry['name'] = steam_id
                entry['steam'] = False
        else:
            
            entry['name'] = steam_id
            entry['steam'] = False
        known_names[steam_id] = entry
        return known_names[steam_id]['name']


def make_safe_filename(name):
    """Replace characters that are not allowed in windows file names."""
    for char in ('/', '\\', ':', '*', '?', '"', '<', '>', '|'):  # Windows illegal folder chars
        if char in name:
            name = name.replace(char, " ")
            # replacables:  ['∕','⧵' ,'˸','⁎','ॽ','“','ᑄ','ᑀ','┃']  #similar chars
    return name


def move_files(steam_id, name, quiet=False):
    """Move all screenshots of a specific game into the corresponding folder."""
    name = make_safe_filename(name)
    newdir = pathlib.Path() / name
    if not newdir.exists():
        newdir.mkdir()
        print(newdir + " was created.")
    for file in newdir.parent.glob(steam_id + "*"):
        shutil.move(file, newdir)
        if not quiet:
            print("{} --> {}".format(file.name, newdir / file.name))


def load_json():
    """Load the translation dictionary."""
    try:
        with open(JSON_FILENAME, "r", encoding="utf8") as file:
            known_names = json.load(file)
            if "version" in known_names:
                if known_names.get("version") < JSON_VERSION:
                    print("Unkown version: {}, current version: {}".format(
                        known_names.get("version"), JSON_VERSION))
                    raise Exception(
                        "Version mismatch. Backup the file and recreate.")
            else:
                print("No version number found")
                known_names = {}
    except FileNotFoundError:
        known_names = {}
    return known_names


def write_json(known_names):
    """Update the translation dictionary."""
    with open(JSON_FILENAME, "w", encoding="utf8") as file:
        known_names.update({"version": JSON_VERSION})
        json.dump(known_names, file, indent="\t")


def main():
    """Sort steam screenshots into a folder structure."""
    arguments = get_arguments()
    known_names = load_json()
    ids = {re.match(r"^(\d+)_.*$", file.name).group(1)
           for file in pathlib.Path().glob("*.png")
           if re.match(r"^(\d+)_.*$", file.name)}
    print("Found IDs:", ids)
    for steam_id in ids:
        if arguments.connect:
            steam_name = get_steam_name(steam_id, known_names)
        else:
            steam_name = steam_id
        if not arguments.json:
            print("Game Name:", steam_name)
            move_files(steam_id, steam_name, arguments.quiet)
    write_json(known_names)


if __name__ == '__main__':
    main()
