from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tree_manager.models import Base

engine = create_engine("sqlite:///database.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
