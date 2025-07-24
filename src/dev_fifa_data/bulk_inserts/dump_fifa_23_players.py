"""
write the fifa 23 player data to the fifa table (SQLite)
note: the fifa 23 player data contains time series data (fifa 23,...,fifa 17 ?) (X) (update 1,...,update n)
"""

FILE_PATH = "C:\\Users\\bokla\\020_Areas\\data\\fifa-data\\data_store\\fifa_23\\male_players.csv"
PATH_DB_FIFA_FULL = "C:\\Users\\bokla\\020_Areas\\data\\fifa-data\\data_store\\fifa-full.db"

import sqlite3
import csv

conn = sqlite3.connect(PATH_DB_FIFA_FULL)
cursor = conn.cursor()

with open(FILE_PATH, 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)

    # get the columns from the first line
    columns = next(reader)

    # skip empty rows (... filters completely empty rows  (=[]) ... for some reason these exist)
    filtered_reader = (row for row in reader if any(row))

    placeholders = ', '.join(['?'] * len(columns))
    insert_query = f"INSERT INTO main.fifa_players ({', '.join(columns)}) VALUES ({placeholders})"

    chunk_size = 10000
    chunk = []
    for i, row in enumerate(filtered_reader):
        # note: some integer columns have '' when not applicable
        processed_row = [None if val == '' else val for val in row]
        chunk.append(processed_row)
        if len(chunk) == chunk_size:
            cursor.executemany(insert_query, chunk)
            conn.commit()
            chunk = []

    # insert remaining rows
    if chunk:
        cursor.executemany(insert_query, chunk)
        conn.commit()

conn.close()
