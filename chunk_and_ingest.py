import itertools as IT
import multiprocessing as mp
import csv
#import random
import time
import io
#import logging
#import pickle
import psycopg2
import hashlib
#from sqlalchemy import create_engine
#import numpy as np
import pandas as pd
#import os

def db_ops(username, hostname, db, pwd):
	connection = psycopg2.connect(user=username, host=hostname, dbname=db, password=pwd)
	cursor = connection.cursor()
	return(cursor, connection)

def trunc(name):
	db_cursor, db_connection = db_ops('postgres', '172.28.1.4', 'postgres', 'postgres')
	db_cursor.execute("truncate table {}".format(name))
	db_cursor.connection.commit()
	db_cursor.close()
	db_connection.close()
	return(name+' Truncated Succesfully')
	
def insert_agg(name):
	query = '''insert into {} (name, number_of_products)
	select name, count(product) from products group by name'''.format(name)
	db_connection = None
	try:
		db_cursor, db_connection = db_ops('postgres', '172.28.1.4', 'postgres', 'postgres')
		db_cursor.connection.commit()
		db_cursor.execute(query)
		db_cursor.connection.commit()
		db_cursor.close()
	except (Exception, psycopg2.DatabaseError) as error:
		print(error)
	finally:
		if db_connection is not None:
			db_connection.close()
	return('Aggregated Data Inserted into '+name)
	
def insert_update_target():
	query = '''with stg as (
select distinct name, sku, description, md5, product
from products_stg
), upd as (
update products tgt
set name = s.name,
product = s.product
from stg s
where (tgt.md5 = s.md5)
returning s.name, s.sku, s.description, s.md5
)
insert into products
select distinct s.name, s.sku, s.description, s.md5, s.product
from products_stg s
left join
upd on
upd.md5=s.md5
where upd.md5 is null'''
	db_connection = None
	try:
		db_cursor, db_connection = db_ops('postgres', '172.28.1.4', 'postgres', 'postgres')
		db_cursor.execute('alter table products drop constraint products_pkey')
		db_cursor.execute('alter table products alter sku drop not null, alter description drop not null, alter md5 drop not null')
		db_cursor.connection.commit()
		db_cursor.execute(query)
		db_cursor.connection.commit()
		db_cursor.execute('alter table products alter sku set not null, alter description set not null, alter md5 set not null')
		db_cursor.execute('alter table products add constraint products_pkey primary key (sku, description)')
		db_cursor.connection.commit()
		db_cursor.close()
	except (Exception, psycopg2.DatabaseError) as error:
		print(error)
	finally:
		if db_connection is not None:
			db_connection.close()
	return('Data inserted in Target table products')
	
def hash(sourcedf,destinationdf,*column):
	columnName = ''
	destinationdf['md5'] = pd.DataFrame(sourcedf[list(column)].values.sum(axis=1))[0].str.encode('utf-8').apply(lambda x: (hashlib.md5(x).hexdigest().upper()))
	
def worker(chunk):
	db_cursor, db_connection = db_ops('postgres', '172.28.1.4', 'postgres', 'postgres')
	str_buffer = io.StringIO()
	df =  pd.DataFrame(chunk)
	df.columns = ['name', 'sku', 'description']
	df.iloc[:, 2] = df.iloc[:, 2].replace(r'\\n',' ', regex=True).replace(r'''.
''', '. ', regex = True)
	hash(df, df, 'sku', 'description')
	df['product'] = df['sku']
	df.to_csv(str_buffer, sep='\t', header=False, index=False)
	str_buffer.seek(0)
	db_cursor.copy_from(str_buffer, 'products_stg', null="")
	db_cursor.connection.commit()
	db_cursor.close()
	db_connection.close()
	
def chunk_it(fname):
	num_procs = mp.cpu_count()
	chunksize = 200000
	
	pool = mp.Pool(num_procs)
	largefile = fname
	results = []
	with open(largefile, 'r') as f:
		reader = csv.reader(f)
		next(reader, None)  # skip the headers
		i=1
		for chunk in iter(lambda: list(IT.islice(reader, chunksize*num_procs)), []):
			chunk = iter(chunk)
			pieces = list(iter(lambda: list(IT.islice(chunk, chunksize)), []))
			pool.map(worker, pieces)
	pool.close()
	pool.join()
	return('data in staging')
	
if __name__ == '__main__':
	stg_name = 'products_stg'
	tgt_name = 'products'
	filename = 'products.csv'
	agg_name = 'products_agg'
	st1 = time.time()
	message1 = trunc(stg_name)
	print(message1)
	msg = chunk_it(filename)
	print(msg)
	et1 = time.time() - st1
	print('staging time: '+str(et1))
	st = time.time()
	message4 = insert_update_target()
	et = time.time() - st
	print('upsert time: '+str(et))
	message2 = trunc(agg_name)
	print(message2)
	st2 = time.time()
	message3 = insert_agg(agg_name)
	print(message3)
	et2 = time.time() - st2
	print('Aggregation table load time: '+str(et2))