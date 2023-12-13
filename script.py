import requests
from bs4 import BeautifulSoup
import mysql.connector
from mysql.connector import errorcode


def scrape(url):
    page = requests.get(url)
    return BeautifulSoup(page.content, 'html.parser')


def parse_html(html):
    table = html.find('tbody')
    rows = table.find_all('tr')

    # Packs stored as 2D array, with the indices identified as such:
    # (0: pack_id, 1: pack_name, 2: coin_value, 3: fcp_value, 4: item_count, 5: rare_item_count, 6: player_count)

    packs = list(list())

    for row in rows:
        pack = []

        ## First element in each row contains pack ID and name

        header = row.find('td', attrs={'class': 'whitespace-nowrap'}).find('a')

        pack_id = header.get('href').split('/')[2]
        pack_name = header.get_text()

        pack.append(pack_id)
        pack.append(pack_name)

        cols = row.find_all('td')[1:]

        for i in range(6):
            ## 5th column is quicksell value, don't need
            if i == 4:
                continue
            attribute = cols[i].get_text()
            if attribute == '-' or attribute == '0':
                attribute = 0
            elif '.' in attribute:
                attribute = -1
            else:
                attribute = int(attribute.replace(',', ''))
            pack.append(attribute)

        packs.append(pack)

    return packs


def create_table(cursor):
    create_table_query = '''CREATE TABLE IF NOT EXISTS packs (
        pack_id INTEGER PRIMARY KEY,
        pack_name VARCHAR(64),
        coin_value INT(8),
        fcp_value INT(8),
        item_count INT(4),
        rare_item_count INT(4),
        player_count INT(4)
    )
    '''

    cursor.execute(create_table_query)

def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE packs DEFAULT CHARACTER SET 'utf8'"
        )
    except mysql.connector.Error as err:
        print(err, '\nContinuing...')


def insert_rows(cursor, pack_list):
    try:
        cursor.execute('USE packs')
    except mysql.connector.Error as err:
        print('Database does not exist. Creating...')
        create_database(cursor)
    create_table(cursor)




html = scrape("https://futmind.com/eafc-24-packs-ultimate-team")
pack_list = parse_html(html)
cnx = mysql.connector.connect(user='root', password='root', host='localhost')
cursor = cnx.cursor()
insert_rows(cursor, pack_list)

