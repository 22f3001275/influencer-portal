from sqlalchemy import create_engine,text

engine = create_engine('sqlite:///main.db',echo=True)

with engine.connect() as connection:
   result = connection.execute(text('select "Connection Successful"'))

   print(result.all())