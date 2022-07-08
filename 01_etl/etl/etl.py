import logging
import time

import psycopg2
from backoff import backoff
from elasticsearch import Elasticsearch, helpers
from esloader import ESLoader
from extractor import Extractor
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from settings import EsSettings, PostgreSettings
from state import JsonFileStorage, State
from transformer import Transformer

logging.basicConfig(filename="log.txt", level=logging.DEBUG)

WAIT_SEC = 2


@backoff()
def create_pg_conn(settings: dict) -> _connection:
    """Создает подключение к Postgre"""
    return psycopg2.connect(**settings, cursor_factory=DictCursor)


@backoff()
def create_es_connection(address):
    """Создаст подключение к ES"""
    connection = Elasticsearch(address)
    logging.debug("Попытка подключения к ES")
    if not connection.ping() or connection is None:
        connection = Elasticsearch(address)
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

        # Инициализируем класс, который преобразует данные из Postgre в подходящую для ES схему
        transformer = Transformer()

        # Подключимся к нашему Elastic Search серверу
        es_settings = EsSettings()
        es_conn = create_es_connection(es_settings.get_full_address())

        # Инициализируем класс, который управляет загрузкой данных в ElasticSearch
        loader = ESLoader(es_conn)

        # Проверяем наличие индекса и создаем его, если индекс отсутствует
        print(es_conn)
        loader.delete_index('movies')
        loader.create_index('movies')

        while True:
            data = extractor.extract_data()

            # Если скрипт не находит измененных данных, то мы ожидаем указанное количество времени и возобновляем поиск
            if data == []:
                logging.debug(f"Актуальных данных нет, спим {WAIT_SEC} секунд")
                time.sleep(WAIT_SEC)
                continue

            validated_data = transformer.transform_record(data)
            loader.bulk_upload(data=validated_data, index='movies', chunk_size=80)
