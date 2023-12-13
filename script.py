import requests
from bs4 import BeautifulSoup
import sqlite3

def scrape(url):
    page = requests.get(url)
    return BeautifulSoup(page.content, 'html.parser')

def parse_html(html):
    table = html.find('tbody')
    rows = table.find_all('tr')

    # creates a list of dictionaries to represent rows with the following keys:
    # pack_id, pack_name, coin_value, fcp_value, item_count, rare_count, player_count, rare_player_count

    packs = list(dict())

    for row in rows:
        header = row.find('td', attrs={'class': 'whitespace-nowrap'}).find('a')
        pack_id = header.get('href').split('/')[2]
        pack_name = header.get_text()

        # packs.append({'pack_id': pack_id, 'pack_name': pack_name, 'coin_value': coin_value, 'fcp_value': fcp_value,
        #               'item_count': item_count, 'rare_count': rare_count, 'player_count': player_count,
        #               'rare_player_count': rare_player_count})

parse_html(scrape("https://futmind.com/eafc-24-packs-ultimate-team"))