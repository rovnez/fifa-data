import csv

import pandas as pd

FILE_PATH = "C:\\Users\\bokla\\020_Areas\\data\\fifa-data\\data_store\\fifa_23\\male_players.csv"


# %% GET NR OF LINES
def count_lines_in_csv(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        for i, _ in enumerate(file, start=1):
            pass
    return i


line_count = count_lines_in_csv(FILE_PATH)

# %%




# %%
def read_chunk(chunk_size=10000):
    with open(FILE_PATH, encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        columns = next(reader)
        # skip empty rows (... filters completely empty rows  (=[]) ... for some reason these exist)
        filtered_reader = (row for row in reader if any(row))
        data = []
        for i, row in enumerate(filtered_reader):
            if i >= chunk_size:
                break
            data.append(row)
        return pd.DataFrame(data=data, columns=columns)


        # # get the columns from the first line
        # columns = next(reader)
        #
        #

        #
        # placeholders = ', '.join(['?'] * len(columns))
        # insert_query = f"INSERT INTO fifa ({', '.join(columns)}) VALUES ({placeholders})"
        #
        # chunk_size = 10000
        # chunk = []
        # for i, row in enumerate(filtered_reader):
        #     processed_row = [None if val == '' else val for val in row]
        #     chunk.append(processed_row)
        #     if len(chunk) == chunk_size:
        #         chunk = []
        #


df = read_chunk()