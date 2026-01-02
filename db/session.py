from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker 
from dotenv import load_dotenv
import os  

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL',echo=True)

engine = create_engine(DATABASE_URL)
Session = sessionmaker()
Base = declarative_base()

def get_db():
    db = Session()
    try: 
        yield db
    finally:
        db.close()