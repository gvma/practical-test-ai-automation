# import sys
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import ProgrammingError

# import psycopg2

def create_database(database_url: str):
    url = make_url(database_url)
    
    db_name = url.database
    url = url.set(database="postgres")  # conecta à instância, não ao banco-alvo

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
    # if len(sys.argv) < 2:
    #     print("Usage: python create_db.py postgresql://user:pass@host:port/dbname")
    #     sys.exit(1)
    
    db_url = "postgresql://postgres:postgres@localhost:5432/practical_test"
    # db_url = sys.argv[1]
    create_database(db_url)
