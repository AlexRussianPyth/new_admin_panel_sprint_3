from validation import EsFilmwork


class Transformer:
    """Преобразует данные из Postgre в подходящий для Elastic формат
    Inputs: Batch of data
    Outpur: Batch of docs in elasticsearch format
    """
    def transform_record(self, records: list) -> list[EsFilmwork]:
        """Преобразует список записей из БД в валидированный список EsFilmwork классов"""
        validated_records = []

        for record in records:
            actors = []
            if record[8]:
                for actor in record[8]:
                    actor_id, actor_name = actor.strip(',').split('|')
                    actors.append({
                        'id': actor_id,
                        'name': actor_name
                    })

            writers = []
            if record[9]:
                for writer in record[9]:
                    writer_id, writer_name = writer.strip(',').split('|')
                    writers.append({
                        'id': writer_id,
                        'name': writer_name
                    })

            record_dict = {
                "id": record[0],
                "imdb_rating": record[3],
                "genre": record[4],
                "title": record[1],
                "description": record[2],
                "director": record[5] if record[5] is not None else [],
                "actors_names": record[6],
                "writers_names": record[7],
                "actors": actors,
                "writers": writers,
            }

            validated_records.append(EsFilmwork(**record_dict))

        return validated_records
