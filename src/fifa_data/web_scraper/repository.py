from abc import ABC, abstractmethod

import sqlite3


class Repository(ABC):

    def __init__(self, batch_name: str):
        self.batch_name = batch_name

    @abstractmethod
    def write_urls(self, urls: list) -> int: ...

    @abstractmethod
    def write_players(self, players): ...


class FakeRepository(Repository):

    def write_urls(self, urls: list):
        raise NotImplementedError

    def write_players(self, players):
        raise NotImplementedError


class SqliteRepository(Repository):

    def __init__(self, db_path, batch_name):
        super().__init__(batch_name)
        self.db_path: str = db_path

    def write_urls(self, urls: list, idx_offset: int = 0):
        params = []
        for idx, url in enumerate(urls):
            parts = [p for p in url.split("/") if p.isdigit()]
            params.append({
                "idx": idx + 1 + idx_offset,
                "url": url,
                "batch_name": self.batch_name,
                "player_id": parts[0],
                "fifa_version": parts[1][:2],
                "fifa_update": parts[1][4:],
            })
        insert_sql = """
                     insert into main.import_player_url (url, batch_name, player_id, fifa_version, fifa_update, idx)
                     values (:url, :batch_name, :player_id, :fifa_version, :fifa_update, :idx) \
                     """
        with sqlite3.connect(f"file:/{self.db_path}", uri=True) as conn:
            cursor = conn.cursor()
            cursor.executemany(insert_sql, params)
            inserted_rows = cursor.rowcount
        return inserted_rows

    def write_players(self, players):
        raise NotImplementedError

    def get_urls_from_in_import(self) -> list:
        with sqlite3.connect(f"file:/{self.db_path}", uri=True) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "select url from main.import_player_url where batch_name = ?",
                (self.batch_name,)
            )
            rows = cursor.fetchall()
        urls = [x[0] for x in rows]
        return urls

    def get_urls_in_core(self) -> list:
        with sqlite3.connect(f"file:/{self.db_path}", uri=True) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "select player_url from main.player_url where player_url.status = 0",
            )
            rows = cursor.fetchall()
        urls = [x[0] for x in rows]
        return urls

    def transfer_urls_from_import_to_core(self):
        with sqlite3.connect(f"file:/{self.db_path}", uri=True) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                           delete
                           from main.player_url
                           where exists ( select 1
                                          from main.import_player_url ipu
                                          where ipu.batch_name = ?
                                            and ipu.player_id = player_url.player_id
                                            and ipu.fifa_version = player_url.fifa_version
                                            and ipu.fifa_update = player_url.fifa_update )
                           """, (self.batch_name,))

            deleted = cursor.rowcount
            cursor.execute("""
                           insert into main.player_url (player_url, player_id, fifa_version, fifa_update, idx)
                           select ipu.url, ipu.player_id, ipu.fifa_version, ipu.fifa_update, ipu.idx
                           from main.import_player_url ipu
                           where ipu.batch_name = ?
                             and not exists ( select 1
                                              from main.player_url
                                              where ipu.player_id = player_url.player_id
                                                and ipu.fifa_version = player_url.fifa_version
                                                and ipu.fifa_update = player_url.fifa_update )
                           """, (self.batch_name,))
            inserted = cursor.rowcount
        conn.commit()
        conn.close()
        return {'deleted': deleted, 'inserted': inserted}

    def write_player_html(self, player_url, player_html):
        with sqlite3.connect(f"file:/{self.db_path}", uri=True) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                           insert into main.import_player (player_url, player_html)
                           values (?, ?)
                           """, (player_url, player_html))
        conn.commit()
        conn.close()

    def get_player_html_from_url(self, player_url):
        with sqlite3.connect(f"file:/{self.db_path}", uri=True) as conn:
            cursor = conn.cursor()

            cursor.execute(
                "select import_player.player_html from main.import_player where import_player.player_url = ?"
                , (player_url,)
            )
            rows = cursor.fetchall()
        conn.commit()
        conn.close()
        if len(rows) > 1:
            print(f"WARNING: {player_url} has multiple HTML entries in database.")
        return rows[0][0]  # double index since we want the first and we are dealing with tuple

    def clear_import_table(self):
        with sqlite3.connect(f"file:/{self.db_path}", uri=True) as conn:
            cursor = conn.cursor()
            cursor.execute("delete from main.import_player_url")
        conn.commit()
        conn.close()

    def clear_core_table(self):
        with sqlite3.connect(f"file:/{self.db_path}", uri=True) as conn:
            cursor = conn.cursor()
            cursor.execute("delete from main.player_url")
        conn.commit()
        conn.close()

    def update_player_url_status(self, player_url) -> int:
        with sqlite3.connect(f"file:/{self.db_path}", uri=True) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """update main.player_url
                   set status = 1
                   where player_url = ?
                """
                , (player_url,)
            )
            updated = cursor.rowcount
        conn.commit()
        conn.close()
        return updated


class CsvRepository(Repository):

    def write_urls(self, urls: list):
        raise NotImplementedError

    def write_players(self, players):
        raise NotImplementedError
