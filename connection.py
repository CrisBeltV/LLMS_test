
import pyodbc

server = '(localdb)\ServidorDemos'
database = 'DB_LLMs_TEST'
username = 'sa'
password = '12345678'
driver= '{ODBC Driver 17 for SQL Server}'  # Puede variar dependiendo de la versión que tengas instalada

connection = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

cursor = connection.cursor()

cursor.execute('SELECT * FROM BOOKSTORE')

for row in cursor:
    print(row)

