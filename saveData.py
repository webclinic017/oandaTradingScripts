import sqlalchemy
from sqlalchemy import create_engine

database_username = 'usuario1'
database_password = 'password'
database_ip       = 'localhost:33063'
database_name     = 'APIData'

from pangres import upsert
def saveReturns(returns,tableName):
   
    returns.index.names = ['dia']
    returns.reset_index(inplace=True)
    returns=returns.set_index(["dia","idStrategy","symbol"],drop=True)
    
    engine = sqlalchemy.create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(database_username, database_password,database_ip, database_name))
    #engine.execute()
    #returns.to_sql(con=database_connection, name=tableName, if_exists='replace',index_label='dia')
    upsert(engine=engine,
       df=returns,
       table_name=tableName,
       if_row_exists='update')