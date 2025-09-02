from fifa_data.config import DB_PATH_SCRAPER
from fifa_data.web_scraper.repository import SqliteRepository
from fifa_data.web_scraper.utils import create_batch_name
from fifa_data.web_scraper.utils import write_to_csv


def export_data(file_path: str):
    batch_name = create_batch_name()
    repo = SqliteRepository(db_path=DB_PATH_SCRAPER, batch_name=batch_name)
    data = repo.get_player_data(fifa_version=25)
    write_to_csv(data, file_path)


export_data(file_path="C:\\Users\\bokla\\020_Areas\\data\\fifa-data\\data_store\\temp.csv")
