import json
from pathlib import Path
import os
import pickle
import backend.models.contract_feature_eng as cfe
import pandas as pd


base_dir = str(Path(os.getcwd()))


def get_players(team):
    with open(base_dir + '/data/rosters.json') as rosters:
        r = json.load(rosters)
        players = r.get(team)
        players.sort()
        return { 'players': players }


def get_contract(team, player):
    salary_cap = 81500000
    model_filepath = base_dir + '/backend/models/contract_gbr.sav'
    gbr = pickle.load(open(model_filepath, 'rb'))
    data = cfe.get_player_features(player)
    pred = gbr.predict(data)
    aav = round(salary_cap * pred[0], 2)
    aav = "$" + f"{aav:,}"
    age, position = get_player_age_and_position(player)
    logo = get_logo(team)

    obj = {
        'team': team,
        'logo': logo,
        'player': player,
        'position': position,
        'age': age,
        'aav': aav
    }
    return obj


def get_player_age_and_position(player):
    df = pd.read_csv(base_dir + '\\data\\all_contracts.csv')
    df = df.loc[df['name'] == player]
    position = df.iloc[0].position
    age = str(df.iloc[0].current_age)
    return age, position


def get_logo(team):
    with open(base_dir + '/data/nhl_logo_urls.json') as logos:
        l = json.load(logos)
        return l.get(team)

# r = get_contract('sabres', 'Jeff Skinner')
# print(str(r))
