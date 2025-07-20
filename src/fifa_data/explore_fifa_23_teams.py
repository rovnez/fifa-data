
import pandas as pd

FILE_PATH = "C:\\Users\\bokla\\020_Areas\\data\\fifa-data\\data_store\\fifa_23\\male_teams.csv"
# %% GET NR OF LINES
with open(FILE_PATH, 'r', encoding='utf-8') as f:
    line_count = sum(1 for _ in f)

# %%

df = pd.read_csv(FILE_PATH)

# %%

FILE_PATH = "C:\\Users\\bokla\\020_Areas\\data\\fifa-data\\data_store\\fifa_23\\male_players.csv"
PATH_DB_FIFA_FULL = "C:\\Users\\bokla\\020_Areas\\data\\fifa-data\\data_store\\fifa-full.db"

import sqlite3
import csv

conn = sqlite3.connect(PATH_DB_FIFA_FULL)


df.to_sql('fifa_teams',conn, if_exists='fail', index=False)