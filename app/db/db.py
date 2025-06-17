from sqlmodel import create_engine
from dotenv import load_dotenv

import os

load_dotenv()

database_user = os.getenv("DATABASE_USER")
database_password = os.getenv("DATABASE_PASSWORD")
database_name = os.getenv("DATABASE_NAME")
database_host = os.getenv("DATABASE_HOST")
database_port = os.getenv("DATABASE_PORT")

if not all([database_user, database_password, database_name, database_host, database_port]):
    raise RuntimeError("One or more database environment variables are not set.")

database_url = (
    f"postgresql://{database_user}:{database_password}"
    f"@{database_host}:{database_port}/{database_name}"
)

database_url = "postgresql://postgres:postgres@localhost:5432/practical_test"

engine = create_engine(database_url)
