from sqlmodel import create_engine
from app.config.settings import settings

database_url = (
    f"postgresql://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}"
    f"@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"
)

# database_url = "postgresql://postgres:postgres@localhost:5432/practical_test"

engine = create_engine(database_url)
