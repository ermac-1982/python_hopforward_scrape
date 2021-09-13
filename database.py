# https://docs.microsoft.com/en-us/azure/azure-sql/database/connect-query-python?tabs=windows

import pyodbc 


server = 'hbanonsql.database.windows.net'
database = 'primary'
username = 'simo'
password = 'Mortalkombat2'   
driver= '{ODBC Driver 17 for SQL Server}'

def azure_db_connect():
    try:
        db =  pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
    except:
        return 0
        
    else:
        return db

if __name__ == '__main__':
    azure_db_connect()