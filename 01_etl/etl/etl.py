import logging
import time

import psycopg2
from backoff import backoff
from db_settings import PostgreSettings
from elasticsearch import Elasticsearch, helpers
from esloader import ESLoader
from extractor import Extractor
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from state import JsonFileStorage, State
from transformer import Transformer

logging.basicConfig(filename="log.txt", level=logging.DEBUG)

WAIT_SEC = 2


@backoff()
def create_pg_conn(settings: dict) -> _connection:
    """Создает подключение к Postgre"""
    return psycopg2.connect(**settings, cursor_factory=DictCursor)


@backoff()
def create_es_connection(socket):
    """Создаст подключение к ES"""
    connection = Elasticsearch(socket)
    logging.debug("Попытка подключения к ES")
    if not connection.ping() or connection is None:
        connection = Elasticsearch(socket)
        logging.debug("Подключение к ES создано")
        return connection
    return connection


if __name__ == '__main__':

    with create_pg_conn(PostgreSettings().dict()) as pg_conn:
        # Запускаем класс, управляющий записями о состояниях
        json_storage = JsonFileStorage('states.json')
        json_storage.create_json_storage()
        state = State(json_storage)

        # Подключаем класс, управляющий выгрузкой данных из Postgre
        extractor = Extractor(pg_conn, state)

        # Подключаем класс, который будет преобразовывать данные из Postgre в подходящую для ES схему
        transformer = Transformer()

        # Подключаем класс, который управляет загрузкой данных в ElasticSearch
        es_conn = create_es_connection("http://127.0.0.1:9200")
        loader = ESLoader(es_conn)

        # Проверяем наличие индекса и создаем его, если индекс отсутствует
        loader.delete_index('movies')
        loader.create_index('movies')

        while True:
            data = extractor.extract_data()
            # Если скрипт не находит измененных данных, то мы ждем указанное количество времени и продолжаем поиск

            if data is False:
                time.sleep(WAIT_SEC)
                logger.debug(f"Актуальных данных нет, спим {WAIT_SEC} секунд")
                continue

            validated_data = transformer.transform_record(data)

            loader.bulk_upload(data=validated_data, index='movies', chunk_size=80)
            time.sleep(5)

