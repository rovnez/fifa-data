from fifa_data.config import DATA_DIR, DB_PATH

import os

import sqlite3
import csv

csv_file_path = os.path.join(DATA_DIR, 'fifa_24', 'male_players.csv')

# use mode rw to prevent the file from being created if missing
conn = sqlite3.connect(f"file:/{DB_PATH}?mode=rw", uri=True)
cursor = conn.cursor()

"""
#check what the file looks like
dat = {}
with open(csv_file_path, encoding='utf-8') as csv_file:
    reader = csv.reader(csv_file)
    for i, row in enumerate(reader):
        dat[i] = row
        if i > 100:
            break
"""

# 24, 23, 22, 21, 20, 19, 18, 17 ... (?)
FIFA_VERSION = 24

with open(csv_file_path, encoding='utf-8') as csv_file:
    reader = csv.reader(csv_file)

    # get the columns from the first line
    columns = next(reader)

    fifa_version_idx = [x[0] for x in enumerate(columns) if x[1] == 'fifa_version'][0]

    # change columns update_as_of -> fifa_update_date
    columns[[x[0] for x in enumerate(columns) if x[1] == 'update_as_of'][0]] = 'fifa_update_date'

    # skip empty rows (filters completely empty rows [] -> for some reason these exist.)
    filtered_reader = (row for row in reader if any(row))

    placeholders = ', '.join(['?'] * len(columns))
    insert_query = f"INSERT INTO fifa_players ({', '.join(columns)}) VALUES ({placeholders})"

    chunk_size = 10000
    chunk = []
    for i, row in enumerate(filtered_reader):
        if int(float(row[fifa_version_idx])) == FIFA_VERSION:
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
