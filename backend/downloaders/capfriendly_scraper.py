from bs4 import BeautifulSoup
import urllib.request
import csv
import pandas as pd

teams = ['flames', 'oilers', 'canadiens', 'senators',  'mapleleafs', 'canucks', 'jets',
        'ducks', 'coyotes', 'avalanche', 'kings', 'wild', 'sharks', 'blues', 'goldenknights',
        'hurricanes', 'blackhawks', 'bluejackets', 'stars', 'redwings', 'panthers', 'predators', 'lightning',
        'bruins', 'sabres', 'devils', 'islanders', 'rangers', 'flyers', 'penguins', 'capitals']

def get_player_info():
    #https://chromedriver.chromium.org/downloads
    names_list = []
    position_list = []
    age_list = []
    for team in teams:
        url = 'https://www.capfriendly.com/teams/' + team
        try:
            team_page = urllib.request.urlopen(url).read()
            html = team_page.decode('utf8')
        except Exception as e:
            print(e)
            print("ERROR: Schedule download for " + url + " failed.")

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
            col_counter = 1
            for col in columns:
                if col_counter==1:
                    # first col is name
                    name = col.find('a').text
                    last_first = name.split(',')
                    name = last_first[1] + ' ' + last_first[0]
                    names_list.append(name.lstrip())
                elif col_counter == 4: #position
                    position = col.find('span').text
                    position_list.append(position)
                elif col_counter == 6: #age
                    age = col.find('span').text
                    age_list.append(age)

                col_counter = col_counter + 1
                if col_counter > 6:
                    break
        print(team)

    return names_list, position_list, age_list

def get_all_contracts():
    contracts_df = pd.DataFrame(columns=['name', 'current_age', 'position', 'type', 'expiration_status',
        'cap_hit_percentage_at_signing', 'signing_date'])
    names, positions, ages = get_player_info()
    for n, p, a in zip(names, positions, ages):
        url = 'https://www.capfriendly.com/players/' + n.lower().replace(' ', '-') \
                                                                .replace('é', 'e') \
                                                                .replace('ö', 'o') \
                                                                .replace('ä', 'a') \
                                                                .replace('è', 'e') \
                                                                .replace('ë', 'e') \
                                                                .replace('ü', 'u') \
                                                                .replace('ū', 'u') \
                                                                .replace('á', 'a') \
                                                                .replace('å', 'a')
        try:
            player_page = urllib.request.urlopen(url).read()
            html = player_page.decode('utf8')
        except Exception as e:
            print(e)
            print("ERROR: Schedule download for " + url + " failed.")

        soup = BeautifulSoup(html, 'html.parser')
        contract_tables = soup.find_all('div', {"class": "contract_cont"})
        for contract in contract_tables:
            divs = contract.find_all('div')
            div_counter = 0
            for d in divs:
                div_counter = div_counter + 1
                #if div_counter==1:
                    #skip
                if div_counter==2:
                    type = d.find('h6').text
                elif div_counter==5:
                    length = d.text.split(':')[1].lstrip().split(' ')[0]
                elif div_counter==6:
                    expiration_status = d.text.split(':')[1].lstrip()
                elif div_counter==10:
                    ch_percent = d.text.split(':')[1].lstrip()
                elif div_counter==11:
                    signing_date = d.text.split(':')[1].lstrip()

            row_to_write = [n, a, p, type, expiration_status, ch_percent, signing_date]
            row_as_series = pd.Series(row_to_write, index=contracts_df.columns)
            contracts_df = contracts_df.append(row_as_series, ignore_index=True)
        print(n)

    print(str(contracts_df))
    contracts_df.to_csv('all_contracts.csv', encoding='utf-8-sig', index=False)

get_all_contracts()
