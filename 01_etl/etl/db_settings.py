import os
import pathlib

import dotenv

dotenv.load_dotenv(os.path.join(pathlib.Path(__file__).parent.parent.absolute(), '.env'))

DB_SCHEMA = os.environ.get('DB_SCHEMA')
SQLITE_DB = os.environ.get('SQLITE_DB_NAME')
POSTGRE_SETTINGS = {
    'database': 'movies_database',
    'user': 'app',
    'password': '123qwe',
    'host': '0.0.0.0',
    'port': '5432',
}
