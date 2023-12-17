import time

import requests
import os
from bs4 import BeautifulSoup
import mysql.connector
from mysql.connector import Error


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


def create_table(connection):
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

    if connection is not None:
        with connection.cursor() as cursor:
            try:
                cursor.execute("USE futmind_parser")
                print("Using Database: futmind_parser")
                cursor.execute("DROP TABLE IF EXISTS packs")
                print("Dropped existing table: packs")
                cursor.execute(create_table_query)
            except Error as e:
                print(f"Create Table Error: {e}")
    else:
        print("create_table: Failed to connect")

    connection.commit()
    print("Table Created")


def create_database(connection):
    if connection is not None:
        with connection.cursor() as cursor:
            try:
                cursor.execute("DROP DATABASE IF EXISTS futmind_parser")
                print("Existing Database Dropped")
                cursor.execute(
                    "CREATE DATABASE futmind_parser DEFAULT CHARACTER SET 'utf8'"
                )
                print("Database Created")
                cursor.execute("USE futmind_parser")
                connection.commit()
            except Error as e:
                print(f"Create Database Error: {e}")
    else:
        print("create_database: Failed to connect")


def insert_rows(connection, pack_list):
    with connection.cursor() as cursor:
        try:
            cursor.execute("USE futmind_parser")
            cursor.executemany(
                """INSERT INTO packs
                    VALUES 
                    (%s, %s, %s, %s, %s, %s, %s)""", pack_list
            )
            connection.commit()
            print("Inserted Rows: ", pack_list)
        except Error as e:
            print(f"Insert Rows Error: {e}")


def create_connection():
    connected = False
    attempts = 0

    while not connected and attempts < 5:
        try:
            connection = mysql.connector.connect(
                host="db",
                port="3306",
                user="root",
                password="password"
            )
            if connection.is_connected():
                print("Connected to MySQL")
                connected = True
                return connection
        except Error as e:
            print(f"Error: {e}")
            attempts += 1
            print("Attempting to reconnect to MySQL")
            time.sleep(5)

    return None


html = scrape("https://futmind.com/eafc-24-packs-ultimate-team")
pack_list = parse_html(html)
connection = create_connection()
create_database(connection)
create_table(connection)
insert_rows(connection, pack_list)
