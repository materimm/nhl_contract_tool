import pandas as pd
from pathlib import Path
import os
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np

###################################################################
## age at signing | prev_1_goals | prev_2_goals | prev_3_goals   ##
## prev_1_assists | prev_2_assists | prev_3_assists              ##
## prev_1_cf | prev_2_cf | prev_3_cf | prev_1_xgf | prev_2_xgf   ##
## prev_3_xgf | is_winger | is_center | is_defender | is_goalie  ##
## is_UFA | prev_1_sh | prev_2_sh | prev_3_sh | expires_as_ufa   ##
###################################################################

def get_age_at_signing(row):
    current_age = row['current_age']
    sign_date = row['signing_date']
    today = dt.date.today()
    years_since_sign = today.year - sign_date.year - ((today.month, today.day) < (sign_date.month, sign_date.day))
    return current_age - years_since_sign


def get_player_status_at_signing(row, contracts_df):
    signing_date = row['signing_date']
    name = row['name']
    if row['type'] == 'ENTRY-LEVEL CONTRACT':
        return 0
    df = contracts_df.loc[contracts_df.name == name]
    found = False
    for index, row in df.iterrows():
        r = row.to_dict()
        if found:
            found = False
            expiration_status = r.get('expiration_status')
            break
        if r.get('signing_date') == signing_date:
            found = True

    if found:
        # there was no previous contract
        return 0
    else:
        return 1 if expiration_status=='UFA' else 0


def get_expiration(row):
    if row['expiration_status'] == 'UFA':
        return 1
    else:
        return 0


def get_is_player_position(row, position):
    p = row['position']
    if position in p:
        return 1
    else:
        return 0


def get_prev_3_years_stats(contracts_df, path):
    stats_dfs_obj = {}
    for y in list(range(2008, 2021)):
        p = path.format(y, y+1)
        df = pd.read_csv(p)
        df = df[['name', 'situation', 'I_F_goals', 'I_F_points', 'icetime',
            'onIce_xGoalsPercentage', 'onIce_corsiPercentage', 'I_F_shotsOnGoal']]
        stats_dfs_obj[str(y) + '-' + str(y+1)] = df

    stats_obj = {
        'p1_goals' : [], 'p2_goals' : [], 'p3_goals' : [],
        'p1_assists' : [], 'p2_assists' : [], 'p3_assists' : [],
        'p1_xgf' : [], 'p2_xgf' : [], 'p3_xgf' : [],
        'p1_corsi' : [], 'p2_corsi' : [], 'p3_corsi' : [],
        'p1_sh' : [], 'p2_sh' : [], 'p3_sh' : []
    }

    for index, row in contracts_df.iterrows():
        r = row.to_dict()
        name = r.get('name')
        name = name.replace('é', 'e') \
                    .replace('ö', 'o') \
                    .replace('ä', 'a') \
                    .replace('è', 'e') \
                    .replace('ë', 'e') \
                    .replace('ü', 'u') \
                    .replace('ū', 'u') \
                    .replace('á', 'a') \
                    .replace('å', 'a')
        sd = r.get('signing_date')
        year = sd.year
        counter = 3
        for y in list(range(year-2, year+1)):
            stats_df = stats_dfs_obj.get(str(y-1) + '-' + str(y))
            stats = stats_df.loc[(stats_df.name==name) & (stats_df.situation=='all')]

            if stats.empty:
                stats_obj['p' + str(counter) + '_goals'].append(0)
                stats_obj['p' + str(counter) + '_assists'].append(0)
                stats_obj['p' + str(counter) + '_xgf'].append(0)
                stats_obj['p' + str(counter) + '_corsi'].append(0)
                stats_obj['p' + str(counter) + '_sh'].append(0)
                counter = counter - 1
                continue

            goals = stats['I_F_goals'].values[0]
            stats_obj['p' + str(counter) + '_goals'].append(goals)
            stats_obj['p' + str(counter) + '_assists'].append(stats['I_F_points'].values[0] - goals)
            stats_obj['p' + str(counter) + '_xgf'].append(stats['onIce_xGoalsPercentage'].values[0])
            stats_obj['p' + str(counter) + '_corsi'].append(stats['onIce_corsiPercentage'].values[0])
            sog = stats['I_F_shotsOnGoal'].values[0]
            sh = 0 if sog==0 else round(goals/sog, 4)
            stats_obj['p' + str(counter) + '_sh'].append(sh)

            counter = counter - 1

    return stats_obj


def format_contract_info():
    base_dir = str(Path(os.getcwd()))#.parents[0])
    contracts_df = pd.read_csv(base_dir + '\\data\\all_contracts.csv')
    contracts_df['signing_date'] = pd.to_datetime(contracts_df.signing_date, errors='coerce')
    contracts_df = contracts_df.sort_values(['name', 'signing_date'], ascending=(True, False))

    contracts_df['age_at_signing'] = contracts_df.apply(lambda row: get_age_at_signing(row), axis=1)
    contracts_df['is_ufa'] = contracts_df.apply(lambda row: get_player_status_at_signing(row, contracts_df), axis=1)
    contracts_df['expires_as_ufa'] = contracts_df.apply(lambda row: get_expiration(row), axis=1)
    contracts_df['is_center'] = contracts_df.apply(lambda row: get_is_player_position(row, 'C'), axis=1)
    contracts_df['is_winger'] = contracts_df.apply(lambda row: get_is_player_position(row, 'W'), axis=1)
    contracts_df['is_defenseman'] = contracts_df.apply(lambda row: get_is_player_position(row, 'D'), axis=1)
    #contracts_df['is_goalie'] = contracts_df.apply(lambda row: get_is_player_position(row, 'G'), axis=1)
    contracts_df['cap_hit_percentage_at_signing'] = contracts_df['cap_hit_percentage_at_signing'].apply(lambda x: x/100)

    contracts_df = contracts_df.loc[contracts_df.type != 'ENTRY-LEVEL CONTRACT']
    contracts_df.drop('current_age', axis=1, inplace=True)
    contracts_df = contracts_df.loc[contracts_df.position != 'G']
    contracts_df.drop('position', axis=1, inplace=True)
    contracts_df.drop('type', axis=1, inplace=True)
    contracts_df.drop('expiration_status', axis=1, inplace=True)
    #filter out contracts signed before 2011 since we dont have 3 years of stats data
    contracts_df = contracts_df[contracts_df['signing_date'].dt.year >= 2011]
    stats_obj = get_prev_3_years_stats(contracts_df, base_dir + '\\data\\moneypuck\\skaters\\{}-{}-skaters.csv')
    contracts_df['prev_1_goals'] = stats_obj['p1_goals']
    contracts_df['prev_2_goals'] = stats_obj['p2_goals']
    contracts_df['prev_3_goals'] = stats_obj['p3_goals']
    contracts_df['prev_1_assists'] = stats_obj['p1_assists']
    contracts_df['prev_2_assists'] = stats_obj['p2_assists']
    contracts_df['prev_3_assists'] = stats_obj['p3_assists']
    contracts_df['prev_1_xgf'] = stats_obj['p1_xgf']
    contracts_df['prev_2_xgf'] = stats_obj['p2_xgf']
    contracts_df['prev_3_xgf'] = stats_obj['p3_xgf']
    contracts_df['prev_1_corsi'] = stats_obj['p1_corsi']
    contracts_df['prev_2_corsi'] = stats_obj['p2_corsi']
    contracts_df['prev_3_corsi'] = stats_obj['p3_corsi']
    contracts_df['prev_1_sh'] = stats_obj['p1_sh']
    contracts_df['prev_2_sh'] = stats_obj['p1_sh']
    contracts_df['prev_3_sh'] = stats_obj['p1_sh']

    contracts_df.to_csv('features.csv', encoding='utf-8-sig', index=False)


def plot_histo():
    base_dir = str(Path(os.getcwd()).parents[0])
    features = pd.read_csv(base_dir + '\\NHLData\\features.csv')
    labels = ['prev_1_goals', 'prev_2_goals', 'prev_3_goals', 'prev_1_assists', 'prev_2_assists', 'prev_3_assists']
    for l in labels:
        stat_arr = features[l].to_list()
        plt.hist(stat_arr, density=True, bins=10)  # density=False would make counts
        plt.ylabel('bin height')
        plt.xlabel('bins');
        plt.title(l)
        plt.show()


def binning(features):
    if features is None:
        base_dir = str(Path(os.getcwd())) #.parents[0])
        features = pd.read_csv(base_dir + '\\data\\features.csv')

    for i in ['1', '2', '3']:
        features['prev_' + i + '_goals_bin_0-9'] = features.apply(lambda row: get_goals_assists_bin(row, 'goals', i, 1), axis=1)
        features['prev_' + i + '_goals_bin_10-19'] = features.apply(lambda row: get_goals_assists_bin(row, 'goals', i, 2), axis=1)
        features['prev_' + i + '_goals_bin_20-29'] = features.apply(lambda row: get_goals_assists_bin(row, 'goals', i, 3), axis=1)
        features['prev_' + i + '_goals_bin_30_up'] = features.apply(lambda row: get_goals_assists_bin(row, 'goals', i, 4), axis=1)

        features['prev_' + i + '_assists_bin_0-9'] = features.apply(lambda row: get_goals_assists_bin(row, 'assists', i, 1), axis=1)
        features['prev_' + i + '_assists_bin_10-19'] = features.apply(lambda row: get_goals_assists_bin(row, 'assists', i, 2), axis=1)
        features['prev_' + i + '_assists_bin_20-29'] = features.apply(lambda row: get_goals_assists_bin(row, 'assists', i, 3), axis=1)
        features['prev_' + i + '_assists_bin_30-49'] = features.apply(lambda row: get_goals_assists_bin(row, 'assists', i, 4), axis=1)
        features['prev_' + i + '_assists_bin_50_up'] = features.apply(lambda row: get_goals_assists_bin(row, 'assists', i, 5), axis=1)

        features['age_bin_under_23'] = features.apply(lambda row: get_age_bin(row, 1), axis=1)
        features['age_bin_23-27'] = features.apply(lambda row: get_age_bin(row, 2), axis=1)
        features['age_bin_28-30'] = features.apply(lambda row: get_age_bin(row, 3), axis=1)
        features['age_bin_30_35'] = features.apply(lambda row: get_age_bin(row, 4), axis=1)
        features['age_bin_35_up'] = features.apply(lambda row: get_age_bin(row, 5), axis=1)

    features.drop('prev_1_goals', axis=1, inplace=True)
    features.drop('prev_2_goals', axis=1, inplace=True)
    features.drop('prev_3_goals', axis=1, inplace=True)
    features.drop('prev_1_assists', axis=1, inplace=True)
    features.drop('prev_2_assists', axis=1, inplace=True)
    features.drop('prev_3_assists', axis=1, inplace=True)
    features.drop('name', axis=1, inplace=True)
    features.drop('signing_date', axis=1, inplace=True)
    features.drop('age_at_signing', axis=1, inplace=True)
    #pretty sure this matters more for term
    #features.drop('expires_as_ufa', axis=1, inplace=True)

    return features
    #features.to_csv('features_bins.csv', encoding='utf-8-sig', index=False)


def get_age_bin(row, bin):
    # Age bins: <23, 23-27, 28-30, 31-35, >35
    age = row['age_at_signing']
    if bin == 1:
        if age < 23:
            return 1
    elif bin == 2:
        if (age < 28) & (age > 22):
            return 1
    elif bin == 3:
        if (age > 27) & (age < 31):
            return 1
    elif bin == 4:
        if (age > 30) & (age < 36):
            return 1
    elif bin == 5:
        if age > 35:
            return 1

    return 0


def get_goals_assists_bin(row, stat, prev, bin):
    # Goals bins: 0-9, 10-19, 20-29, >=30
    if stat == 'goals':
        g = row['prev_' + prev + '_' + stat]
        if bin == 1:
            if g <= 9:
                return 1
        elif bin == 2:
            if (g >= 10) & (g <= 19):
                return 1
        elif bin == 3:
            if (g >= 20) & (g <=29):
                return 1
        elif bin == 4:
            if g >= 30:
                return 1

    # Assists bins: 0-9, 10-19, 20-29, 30-49, >=50
    if stat == 'assists':
        a = row['prev_' + prev + '_' + stat]
        if bin == 1:
            if a <= 9:
                return 1
        elif bin == 2:
            if (a >= 10) & (a<=19):
                return 1
        elif bin == 3:
            if (a >= 20) & (a<=29):
                return 1
        elif bin == 4:
            if (a >= 30) & (a<=49):
                return 1
        elif bin == 5:
            if (a >= 50):
                return 1

    return 0


def get_player_features(name):
    base_dir = str(Path(os.getcwd())) #.parents[0])
    player_df = pd.read_csv(base_dir + '\\data\\all_contracts.csv')
    player_df = player_df.loc[player_df.name==name]
    player_df['signing_date'] = pd.to_datetime(player_df.signing_date)
    player_df = player_df[player_df.signing_date == player_df.signing_date.max()]
    player_df['is_ufa'] = 1 if player_df.iloc[0]['expiration_status'] == 'UFA' else 0
    player_df['age_at_signing'] = player_df.iloc[0]['current_age']
    player_df['is_center'] = player_df.apply(lambda row: get_is_player_position(row, 'C'), axis=1)
    player_df['is_winger'] = player_df.apply(lambda row: get_is_player_position(row, 'W'), axis=1)
    player_df['is_defenseman'] = player_df.apply(lambda row: get_is_player_position(row, 'D'), axis=1)
    player_df.drop('current_age', axis=1, inplace=True)
    player_df.drop('position', axis=1, inplace=True)
    player_df.drop('type', axis=1, inplace=True)
    player_df.drop('expiration_status', axis=1, inplace=True)
    player_df.drop('cap_hit_percentage_at_signing', axis=1, inplace=True)

    path = base_dir + '\\data\\moneypuck\\skaters\\{}-{}-skaters.csv'
    counter = 3
    this_year = dt.date.today().year
    for y in list(range(this_year-3, this_year)):
        p = path.format(y, y+1)
        stats_df = pd.read_csv(p)
        stats_df = stats_df[['name', 'situation', 'I_F_goals', 'I_F_points', 'icetime',
            'onIce_xGoalsPercentage', 'onIce_corsiPercentage', 'I_F_shotsOnGoal']]
        stats_df = stats_df.loc[(stats_df.name==name) & (stats_df.situation=='all')]

        if stats_df.empty:
            player_df['prev_' + str(counter) + '_goals'] = 0
            player_df['prev_' + str(counter) + '_assists'] = 0
            player_df['prev_' + str(counter) + '_xgf'] = 0
            player_df['prev_' + str(counter) + '_corsi'] = 0
            player_df['prev_' + str(counter) + '_sh'] = 0
            counter = counter - 1
            continue

        goals = stats_df['I_F_goals'].values[0]
        player_df['prev_' + str(counter) + '_goals'] = goals
        player_df['prev_' + str(counter) + '_assists'] = stats_df['I_F_points'].values[0] - goals
        player_df['prev_' + str(counter) + '_xgf'] = stats_df['onIce_xGoalsPercentage'].values[0]
        player_df['prev_' + str(counter) + '_corsi'] = stats_df['onIce_corsiPercentage'].values[0]
        sog = stats_df['I_F_shotsOnGoal'].values[0]
        sh = 0 if sog==0 else round(goals/sog, 4)
        player_df['prev_' + str(counter) + '_sh'] = sh
        counter = counter - 1

    return binning(player_df)


# Step 1: download moneypuck skater data (moneypuck_dowloader.py)
# Step 2: download capfriendly contract (capfiendly_scraper.py)
# Step 3: format contract info -> features.csv
#format_contract_info()
# Step 4 use tthe get_player_features() funtion to get features to pass to model
#get_player_features('Jeff Skinner')
