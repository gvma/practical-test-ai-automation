from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import ProgrammingError

def create_database(database_url: str):
    url = make_url(database_url)
    
    db_name = url.database
    url = url.set(database="postgres")

    engine = create_engine(url)
    conn = engine.connect()
    conn.execution_options(isolation_level="AUTOCOMMIT")

    try:
        conn.execute(text(f"CREATE DATABASE {db_name}"))
        print(f"Database '{db_name}' created.")
    except ProgrammingError as e:
        if 'already exists' in str(e):
            print(f"Database '{db_name}' already exists.")
        else:
            raise
    finally:
        conn.close()


if __name__ == "__main__":
    db_url = "postgresql://postgres:postgres@postgres-service:5432/practical_test"
    create_database(db_url)
