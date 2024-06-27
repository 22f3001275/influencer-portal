from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
# from db.connect import Base

engine = create_engine('sqlite:///main.db', echo=True)
with engine.connect() as connection:
    result = connection.execute(text('select "Connection Successful"'))
    # Base.metadata.create_all(bind=engine)
    print(result.all())

session = Session(bind=engine)
