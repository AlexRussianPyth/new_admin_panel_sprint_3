import datetime
from typing import List

from backoff import backoff
from psycopg2.extensions import connection as _connection
from utils import ornate_ids


class Extractor:
    """ Вытаскивает из Postgre записи по разным сущностям"""
    def __init__(self, connection: _connection, state_manager):
        self.connection = connection
        self.state_manager = state_manager

    def execute_query(self, query: str):
        curs = self.connection.cursor()
        curs.execute(query)
        return curs

    def update_modified_field(self, ids: str, table: str) -> None:
        """Обновляет поля modified на текущую дату и время"""

        sql = f"""
                    UPDATE content.{table}
                    SET modified = '{str(datetime.datetime.now())}'
                    WHERE id IN ({ids});
                """

        self.execute_query(sql)
        self.connection.commit()

    @backoff()
    def extract_data(self, batch_size=100):
        """Выбирает сущность, которую не обновляли дольше всего, и запускает для нее метод обновления данных
        Returns: Список измененных фильмов со всеми связанными данными о людях и жанрах
        """

        last_film_check = self.state_manager.get_state("last_film_work_check")
        last_genre_check = self.state_manager.get_state("last_genre_check")
        last_person_check = self.state_manager.get_state("last_person_check")

        if last_film_check <= last_person_check and last_film_check <= last_genre_check:
            films = self.get_modified(table="film_work", date=last_film_check, batch_size=batch_size)
        elif last_person_check <= last_genre_check:
            persons = self.get_modified(table="person", date=last_person_check, batch_size=batch_size)
            films = self.find_person_film_connection(persons)
        else:
            genres = self.get_modified(table="genre", date=last_genre_check, batch_size=batch_size)
            films = self.find_genre_film_connection(genres)

        full_data = self.enrich_modified_films(films)

        return full_data

    def get_modified(self, table: str, date: str, batch_size: int) -> List[List]:

        query = f'''
        SELECT id, modified
        FROM content.{table}
        WHERE modified > '{date}'
        ORDER BY modified
        LIMIT {batch_size};
        '''

        curs = self.execute_query(query)
        query_result = curs.fetchall()

        # Так как пачка отсортирована, нам нужно получить самую старую дату из пачки и переставить наше состояние
        self.state_manager.set_state(f"last_{table}_check", str(query_result[0][1]))

        # Получаем строку с id, находящимися в нашем курсоре
        ids = ','.join(curs.mogrify('%s', (item['id'],)).decode()
                       for item in query_result)

        # Обновляем поле modified для каждого объекта, который мы выгрузили из БД
        self.update_modified_field(ids, table)

        return query_result

    def find_person_film_connection(self, modified_persons):

        person_ids = [obj[0] for obj in modified_persons]
        id_string = ornate_ids(person_ids)

        query = f"""
        SELECT fw.id, fw.modified
        FROM content.film_work AS fw
        LEFT JOIN content.person_film_work AS pfw ON pfw.film_work_id = fw.id
        WHERE pfw.person_id IN ({id_string})
        ORDER BY fw.modified;
        """

        curs = self.execute_query(query)
        films = curs.fetchall()

        return films

    def find_genre_film_connection(self, modified_genres):

        genre_ids = [obj[0] for obj in modified_genres]
        id_string = ornate_ids(genre_ids)

        query = f"""
        SELECT fw.id, fw.modified
        FROM content.film_work AS fw
        LEFT JOIN content.genre_film_work AS gfw ON gfw.film_work_id = fw.id
        WHERE gfw.genre_id IN ({id_string})
        ORDER BY fw.modified;
        """

        curs = self.execute_query(query)
        films = curs.fetchall()

        return films

    def enrich_modified_films(self, modified_films: list):

        films_ids = [obj[0] for obj in modified_films]
        id_string = ornate_ids(films_ids)

        query = f"""
        SELECT fw.id as filmwork_id, fw.title, fw.description, fw.rating,
               ARRAY_AGG(DISTINCT g.name) AS genre,
               ARRAY_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'director') AS director,
               ARRAY_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'actor') AS actors_names,
               ARRAY_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'writer') AS writers_names,
               ARRAY_AGG(DISTINCT p.id || '|' || p.full_name) FILTER (WHERE pfw.role = 'actor') AS actors,
               ARRAY_AGG(DISTINCT p.id || '|' || p.full_name) FILTER (WHERE pfw.role = 'writer') AS writers
        FROM content.film_work AS fw
        LEFT JOIN content.person_film_work AS pfw ON pfw.film_work_id = fw.id
        LEFT JOIN content.person AS p ON p.id = pfw.person_id
        LEFT JOIN content.genre_film_work AS gfw ON gfw.film_work_id = fw.id
        LEFT JOIN content.genre AS g ON g.id = gfw.genre_id
        WHERE fw.id IN ({id_string})
        GROUP BY fw.id;
        """

        curs = self.execute_query(query)
        enriched_films = curs.fetchall()

        return enriched_films
