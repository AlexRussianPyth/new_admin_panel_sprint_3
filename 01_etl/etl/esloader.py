from es_index import es_index_schema


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
            print("Ошибка с созданием индекса")
            print(str(ex))
        finally:
            return created

    def store_or_update_doc(self, record, index_name="movies"):
        """Проверит существование документа в индексе. Если документ существует, то обновит его. Если документа
        нет, то создаст новый документ"""
        try:
            self._es.index(index=index_name, id=record.id, document=record.json())
        except Exception as ex:
            print('Ошибка добавления документа в индекс ES')
            print(str(ex))

    def delete_index(self, index_name):
        self._es.options(ignore_status=[400, 404]).indices.delete(index=index_name)
