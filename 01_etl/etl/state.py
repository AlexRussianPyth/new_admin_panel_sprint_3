import abc
import json
from typing import Any, Optional


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        pass

    @abc.abstractmethod
    def retrieve_state(self, key) -> dict:
        pass


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path

    def save_state(self, state: dict) -> None:
        """Save state in permanent JSON storage"""
        with open(self.file_path, "r+") as file:
            json_object = json.load(file)
            json_object[list(state.keys())[0]] = list(state.values())[0]
            file.seek(0)
            json.dump(json_object, file)
            file.truncate()

    def retrieve_state(self, key) -> dict:
        """Download state for specific key from permanent JSON storage.
        Returns empy dict if there are no state for this key"""
        with open(self.file_path, "r") as file:
            json_object = json.load(file)
        state = json_object.get(key)
        return state


class State:
    def __init__(self, storage: BaseStorage):
        self.storage = storage
        self.local_storage = {}

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа"""
        self.local_storage[key] = value
        self.storage.save_state({key: value})

    def get_state(self, key: str) -> Any:
        """Получить состояние по определённому ключу"""
        state = self.storage.retrieve_state(key)
        return state if state else None
