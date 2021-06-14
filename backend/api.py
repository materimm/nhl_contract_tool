import json
from pathlib import Path
import os

base_dir = str(Path(os.getcwd()))

def get_players(team):
    with open(base_dir + '/data/rosters.json') as rosters:
        r = json.load(rosters)
        players = r.get(team)
        players.sort()
        return { 'players': players }


def get_contract(team, player):
    salary_cap = 81500000
    aav = '5000000'

    obj = {
        'team': team,
        'logo': 'http://peter-tanner.com/moneypuck/logos/BUF.png',
        'player': player,
        'position': 'C',
        'age': 27,
        'aav': aav
    }
    return obj
