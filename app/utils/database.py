from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pyodbc

# Using SQL Server, You can use another database connection as well
# Menggunakan SQL Server, Anda juga bisa menggunakan koneksi database lainnya
DATABASE_URL = "mssql+pyodbc://username:password@127.0.0.1/icore?driver=ODBC+Driver+17+for+SQL+Server"

# Initialize the SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
