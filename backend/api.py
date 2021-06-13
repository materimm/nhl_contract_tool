import json
from pathlib import Path
import os

base_dir = str(Path(os.getcwd()))

def get_players(team):
    with open(base_dir + '/data/rosters.json') as rosters:
        r = json.load(rosters)
        players = r.get(team)
        return { 'players': players }
