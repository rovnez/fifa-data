import os

VERBOSE = True

CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.abspath(os.path.join(CONFIG_DIR, '..', '..'))
DATA_DIR = os.path.join(REPO_DIR, 'data_store')

DB_PATH = os.path.join(DATA_DIR, 'fifa-data-science.db')

if VERBOSE:
    print('CONFIG_DIR: ', CONFIG_DIR)
    print('REPO_DIR: ', REPO_DIR)
    print('DATA_DIR: ', DATA_DIR)
    print('DB_PATH: ', DB_PATH)
