from sqlalchemy.orm import Session
from db.connect import engine

session = Session(bind=engine)
