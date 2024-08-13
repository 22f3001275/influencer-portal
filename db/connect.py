from sqlalchemy import create_engine, text
# from models import Base

engine = create_engine('sqlite:///db/main.db', echo=True)

with engine.connect() as connection:
    result = connection.execute(text('select "Connection Successful"'))
    # Base.metadata.create_all(bind=engine)
    print(result.all())
