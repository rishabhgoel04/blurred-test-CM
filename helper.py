import psycopg2 as pg
import time,os
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()


POSTGRES = {
    'user': os.getenv('DBUSER'),
    'pw': os.getenv('DBPASS'),
    'host': os.getenv('DBURL'), 
    'port': os.getenv('PORT'), 
    'db' : os.getenv('DB'),
}

def data_from_db(query):
    input_time = time.time()
    engine = create_engine('postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES)
    connection = engine.connect()
    print("Connected to DB")
    df = pd.read_sql_query(query, con = connection)
    final_time = time.time()
    print('Data retrieved in ' + str(final_time - input_time) + 'seconds' )
    connection.close()
    return df

# def get_data_cmdb(query):    
#     input_time = time.time()
#     conn = pg.connect(host=host,database=db,port=port,user=dbuser,password=dbpass)
#     print('Connected to Replica DB')
#     df = pd.read_sql_query(query, con = conn)       
#     print('Number of rows in Data - ' + str(df.shape[0]))    
#     final_time = time.time()
#     print('Data retrieved in ' + str(final_time - input_time) + 'seconds' )
#     conn.close()
#     return df


def paste_data_google_sheet(df, key,worksheet,add_data_row = 1, add_data_col = 1):
    gc = gspread.service_account(filename='test.json')
    sh = gc.open_by_key(key)
    worksheet = sh.worksheet(worksheet)
    print('Worksheet Connection Established')
    worksheet.clear()
    print('Worksheet Cleared')
    set_with_dataframe(worksheet,df,row=add_data_row, col=add_data_col)
    print('Data Inserted in Google Sheet')




