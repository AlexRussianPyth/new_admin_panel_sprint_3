import logging

from validation import EsFilmwork


class Transformer:
    """Преобразует данные из Postgre в подходящий для Elastic формат.
    Inputs: Batch of records from Postgre
    Outpur: Batch of docs in elasticsearch format
    """
    def transform_record(self, records: list) -> list[EsFilmwork]:
        """Преобразует список записей из БД в валидированный список EsFilmwork классов"""
        validated_records = []

        for record in records:

            actors = []
            if record['actors']:
                for actor in record['actors']:
                    actor_id, actor_name = actor.strip(',').split('|')
                    actors.append({
                        'id': actor_id,
                        'name': actor_name
                    })

            writers = []
            if record['writers']:
                for writer in record['writers']:
                    writer_id, writer_name = writer.strip(',').split('|')
                    writers.append({
                        'id': writer_id,
                        'name': writer_name
                    })

            record_dict = {
                "id": record['filmwork_id'],
                "imdb_rating": record['rating'],
                "genre": record['genre'],
                "title": record['title'],
                "description": record['description'],
                "director": record['director'] if record['director'] is not None else [],
                "actors_names": record['actors_names'],
                "writers_names": record['writers_names'],
                "actors": actors,
                "writers": writers,
            }

            validated_records.append(EsFilmwork(**record_dict))

        logging.debug("Возвращаем обработанную трансформером пачку данных для ES")
        return validated_records
