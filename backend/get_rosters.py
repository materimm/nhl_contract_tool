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
            continue
        elif r.has_attr('class') and r['class'][0] == 'total':
            total_count = total_count + 1
            #total row
            continue
        elif not r.has_attr('class'):
            #spacer row
            continue

        if total_count == 3:
            #we've hit the total row for forwards, d and goalies so we can break
            #dont really care about the taxi squad and buyouts rn
            break

        columns = r.find_all('td')
        col = columns[0] # first col is name
        name = col.find('a').text
        last_first = name.split(',')
        name = last_first[1] + ' ' + last_first[0]
        names_list.append(name.lstrip())

    rosters[t] = names_list

print(str(rosters))

#TODO write out fails
# base_dir = str(Path(os.getcwd()).parents[0])
# with open(base_dir + '/data/rosters.json') as r:
#     json.dump(rosters, r)
