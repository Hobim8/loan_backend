from db.session import Base, engine
import db.models

def init_db():
    print('...connecting to database')
    Base.metadata.create_all(bind=engine)
    print('successsfully created')

if __name__ == '__main__':
    init_db()
