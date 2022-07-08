from es_index import es_index_schema
from elasticsearch import helpers
from typing import List, Iterator


class ESLoader:
    """Загружает данные в Elastic Search"""
    def __init__(self, es_connection):
        self._es = es_connection

    def create_index(self, index_name='movies'):
        created = False
        index_settings = es_index_schema

        try:
            if not self._es.indices.exists(index=index_name):
                # 400 ошибка это IndexAlreadyExists
                self._es.indices.create(index=index_name, ignore=400, body=index_settings)
            created = True
        except Exception as ex:
            logging.debug("Ошибка в создании индекса")
            logging.debug(str(ex))
        finally:
            return created

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

    def delete_index(self, index_name):
        self._es.options(ignore_status=[400, 404]).indices.delete(index=index_name)
