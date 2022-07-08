import logging
from typing import Iterator, List

from elasticsearch import Elasticsearch, TransportError, helpers

from backoff import backoff
from es_index import es_index_schema


class ESLoader:
    """Загружает данные в Elastic Search"""
    def __init__(self, address):
        self.address = address
        self._es = self.connect(address)

    @backoff()
    def connect(self, address) -> Elasticsearch:
        """Вернуть текущее подключение для ES или инициализировать новое"""
        logging.debug("Попытка подключения к ES")
        return Elasticsearch(address)

    @backoff()
    def create_index(self, index_name='movies'):
        created = False
        index_settings = es_index_schema

        try:
            if not self._es.indices.exists(index=index_name):
                # 400 ошибка это IndexAlreadyExists
                self._es.indices.create(index=index_name, ignore=400, body=index_settings)
            created = True
        except TransportError as ex:
            logging.warning("Ошибка в создании индекса")
            logging.warning(str(ex))
        finally:
            return created

    @backoff()
    def bulk_upload(self, data: List, index: str, chunk_size: int) -> None:
        """Загрузит данные из итератора в ES"""

        def generate_data(objects) -> Iterator:
            for obj in objects:
                yield {
                    "_id": obj.id,
                    "_source": obj.dict()
                }

        helpers.bulk(
            self._es,
            actions=generate_data(data),
            index=index,
            chunk_size=chunk_size
        )

    @backoff()
    def delete_index(self, index_name):
        self._es.options(ignore_status=[400, 404]).indices.delete(index=index_name)
