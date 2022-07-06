def ornate_ids(ids_list) -> str:
    """Приводит лист с ID к удобному для Postgre формату:
    'id', 'id', ...
    """

    marked_list = ["'" + id + "'" for id in ids_list]

    id_string = ",".join(marked_list)
    return id_string
