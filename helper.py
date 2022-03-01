import psycopg2 as pg
import time
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from sqlalchemy import create_engine



def get_data_cmdb(query):    
    input_time = time.time()
    conn = pg.connect(host="13.232.92.91",database="cmdb",port="5432",user="cm",password="cm")
    print('Connected to Replica DB')
    df = pd.read_sql_query(query, con = conn)       
    print('Number of rows in Data - ' + str(df.shape[0]))    
    final_time = time.time()
    print('Data retrieved in ' + str(final_time - input_time) + 'seconds' )
    conn.close()
    return df


def paste_data_google_sheet(df, key,worksheet,add_data_row = 1, add_data_col = 1):
    gc = gspread.service_account(filename='test.json')
    sh = gc.open_by_key(key)
    worksheet = sh.worksheet(worksheet)
    print('Worksheet Connection Established')
    worksheet.clear()
    print('Worksheet Cleared')
    set_with_dataframe(worksheet,df,row=add_data_row, col=add_data_col)
    print('Data Inserted in Google Sheet')





def get_data_redshift(query):
    attempts = 0
    input_time = time.time()
    conn = pg.connect(host="cm-redshift-1.cyl4ilkelm5m.ap-south-1.redshift.amazonaws.com",database="cmwh",port="5439",user="cmrsreader",password="^ft@F2w8N2KQeX!")
    print('Connected to Replica DB')
    df = pd.read_sql_query(query, con = conn)
    print('Number of rows in Data - ' + str(df.shape[0]))
    final_time = time.time()
    print('Data retrieved in ' + str(final_time - input_time) + 'seconds' )
    conn.close()
    return df




def get_data_crmdb(query):
    input_time = time.time()
    conn = pg.connect(host="cmdb-rr.cbo3ijdmzhje.ap-south-1.rds.amazonaws.com",database="crmdb",port="5432",user="crm_readonly",password="crm_readonly")
    print('Connected to Replica DB')
    df = pd.read_sql_query(query, con = conn)
    print('Number of rows in Data - ' + str(df.shape[0]))
    final_time = time.time()
    print('Data retrieved in ' + str(final_time - input_time) + 'seconds' )
    return df




def get_data_wms(query):
    input_time = time.time()
    conn = pg.connect(host="cmdb-rr.cbo3ijdmzhje.ap-south-1.rds.amazonaws.com",database="wmsdb",port="5432",user="wms",password="wms")
    print('Connected to Replica DB')
    df = pd.read_sql_query(query, con = conn)
    print('Number of rows in Data - ' + str(df.shape[0]))
    final_time = time.time()
    print('Data retrieved in ' + str(final_time - input_time) + 'seconds' )
    return df




def execute_statement_production(query):
    ## Writing to db
    engine = create_engine('postgresql://cm:cm@cmdb.cbo3ijdmzhje.ap-south-1.rds.amazonaws.com:5432/cmdb')

    print('DB Connection Established')

    engine.execute(query)

    print('Finished Executing Statement')



def write_data_production(df, table_name, if_exists_record = 'append', db_schema = 'public'):
    ## Writing to db
    from sqlalchemy import create_engine
    engine = create_engine('postgresql://cm:cm@cmdb.cbo3ijdmzhje.ap-south-1.rds.amazonaws.com:5432/cmdb')

    print('DB Conncetion Established')

    df.to_sql(table_name, engine, if_exists= if_exists_record, index=False, schema= db_schema)

    print('Finished Writing to DB')



