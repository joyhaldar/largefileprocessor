# largefileprocessor
This is an assignment for the Data Engineer Position at Postman.


Steps to setup (I used GitBash on Windows to execute the below commands):

1) git clone https://github.com/joyhaldar/largefileprocessor.git
2) cd largefileprocessor
3) docker-compose build
4) docker-compose up -d
5) Don't close the terminal id not using '-d' flag in above command.


Steps to Create the tables:

1) Open a new terminal/GitBash terminal.
2) docker exec largefileprocessor_postgres_1 -it bash
3) cd /var/www/html
4) python3 create_tables.py


Steps to query the tables:

1) docker exec largefileprocessor_postgres_1 -it bash
2) psql -U postgres -d postgres.
3) select * from products_stg;  (Staging Table with no constraints)
4) select * from products;  (Target table)
5) select * from products_agg;  (Aggregated table with Names and Number of Products)

Steps to run the ingestion program:

1) docker exec largefileprocessor_postgres_1 -it bash
2) cd /var/www/html
3) python3 chunk_and_ingest.py














