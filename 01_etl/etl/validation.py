from typing import Optional

from pydantic import BaseModel


class Person(BaseModel):
    id: str
    name: str


class EsFilmwork(BaseModel):
    id: str
    imdb_rating: Optional[float]
    genre: list[str]
    title: str
    description: Optional[str]
    director: Optional[list[str]]
    actors_names: Optional[list[str]]
    writers_names: Optional[list[str]]
    actors: Optional[list[Person]]
    writers: Optional[list[Person]]
