import os
import pathlib
from pydantic import BaseSettings, Field

import dotenv

dotenv.load_dotenv(os.path.join(pathlib.Path(__file__).parent.parent.absolute(), '.env'))


class PostgreSettings(BaseSettings):
    database: str = Field(..., env='POSTGRES_DB')
    user: str = Field(..., env='POSTGRES_USER')
    password: str = Field(..., env='POSTGRES_PASSWORD')
    host: str = Field(..., env='DB_HOST')
    port: str = Field(..., env='DB_PORT')

    class Config:
        env_file = '../.env'
        env_file_encoding = 'utf-8'
