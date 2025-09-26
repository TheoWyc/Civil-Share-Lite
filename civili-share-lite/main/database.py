from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# URL de la base (fichier SQLite nommé notes.db)
SQLALCHEMY_DATABASE_URL = "sqlite:///./notes.db"

# echo=True affiche les requêtes SQL dans la console
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()

# Dépendance : obtenir une session DB dans les routes FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
