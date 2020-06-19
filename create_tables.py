import psycopg2
import time
	
st = time.time()
db_connection = psycopg2.connect(user='postgres', host='172.28.1.4', dbname='postgres', password='postgres')
db_cursor = db_connection.cursor()
db_cursor.execute('''CREATE TABLE products_stg (
  name varchar(255) ,
  sku varchar(255) ,
  description varchar(255) ,
  md5 uuid , 
  product varchar(255) 
)''')
db_cursor.execute('''CREATE TABLE products (
  name varchar(255) ,
  sku varchar(255) NOT NULL,
  description varchar(255) NOT NULL,
  md5 uuid NOT NULL,
  product varchar(255),
  PRIMARY KEY (sku, description)
)''')
db_cursor.execute('''CREATE TABLE products_agg (
  name varchar(255) ,
  number_of_products int
)''')
db_cursor.connection.commit()
db_cursor.close()
db_connection.close()
et = time.time() - st
print(et)