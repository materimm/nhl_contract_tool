import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
import os

teams = ['flames', 'oilers', 'canadiens', 'senators',  'mapleleafs', 'canucks', 'jets',
        'ducks', 'coyotes', 'avalanche', 'kings', 'wild', 'sharks', 'blues', 'goldenknights',
        'hurricanes', 'blackhawks', 'bluejackets', 'stars', 'redwings', 'panthers', 'predators', 'lightning',
        'bruins', 'sabres', 'devils', 'islanders', 'rangers', 'flyers', 'penguins', 'capitals']
url = 'https://www.capfriendly.com/teams/{}'
rosters = {}

for t in teams:
    print(t)
    names_list = []
    formatted_url = url.format(t)
    r = requests.get(formatted_url, allow_redirects=True)
    html = r.content.decode('utf8')
    soup = BeautifulSoup(html, 'html.parser')
    team_table = soup.find('table', id="team")
    rows = team_table.find_all('tr')
    total_count = 0
    for r in rows:
        if r.has_attr('class') and r['class'][0] == 'column_head':
            #header row
            columns = r.find_all('td')
            col = columns[0]
            if 'RETAINED SALARY' in col.text or 'BUYOUT HISTORY' in col.text:
                #we've passed all player tables
                break
            else:
                continue
        elif r.has_attr('class') and r['class'][0] == 'total':
            total_count = total_count + 1
            #total row
            continue
        elif not r.has_attr('class'):
            #spacer row
            continue

        if total_count == 3:
            #skip the goalies
            #TODO skip doesnt work
            continue

        if total_count == 5:
            #we've hit the tables for forwards, d, goalies, LTIR and taxi squad so we can break
            #dont really care about buried and buyouts
            break

        columns = r.find_all('td')
        col = columns[0] # first col is name
        name = col.find('a').text
        last_first = name.split(',')
        name = last_first[1] + ' ' + last_first[0]
        name = name.replace('é', 'e') \
                    .replace('ö', 'o') \
                    .replace('ä', 'a') \
                    .replace('è', 'e') \
                    .replace('ë', 'e') \
                    .replace('ü', 'u') \
                    .replace('ū', 'u') \
                    .replace('á', 'a') \
                    .replace('å', 'a')
        names_list.append(name.lstrip())

    rosters[t] = names_list

print(str(rosters))

#TODO write out fails
# base_dir = str(Path(os.getcwd()).parents[0])
# with open(base_dir + '/backend/rosters.json') as r:
#     json.dump(rosters, r)
