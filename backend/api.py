import json
import os

base_dir = os.getcwd().parents[0]

get_players(team):
    with open(base_dir + '/data/rosters.json') as rosters:
        r = json.load(rosters)
        return r.get(team)
