# largefileprocessor
This is an assignment for the Data Engineer Position at Postman.


Steps to setup the docker image(I used GitBash on Windows to execute the below commands):

1) git clone https://github.com/joyhaldar/largefileprocessor.git
2) cd largefileprocessor
3) Please place the csv file 'products.csv' in this folder.
4) docker-compose build
5) docker-compose up -d
6) Don't close the terminal id not using '-d' flag in above command.


Steps to Create the tables (postgres and python inside docker):

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




Details of all the tables and their schema, [with commands to recreate them] (Note: The Tables have already been created in 'Steps to Create the tables' above)

'products_stg':
  This is the staging table. The csv file is parallely processed and bulk loaded into this table and it has no constraints applied on     it.

  Column Details:
    name: mapped to 'name' in csv file.
    sku: mapped to 'sku' in csv file.
    description: mapped to 'description' in csv file.
    md5: an md5 hashcode created in script on 'sku' and 'description' (which was the unique combination) to create a unique code for              each unique value. This column is used for joining the staging and target tables during the update/insert process as it less in          size and is always unique based on th condition.
    product: copy of the 'sku' column, as 'sku' is part of the PK, this column would be used for updates.
    
    CREATE TABLE products_stg (
                 name varchar(255) ,
                 sku varchar(255) ,
                 description varchar(255) ,
                 md5 uuid , 
                 product varchar(255) 
                );
                
'products':
  This is the target table. The data from the staging table is put into this table using an update/insert script in the ingestion         program. This table is never truncated.

  Column Details:
    name: mapped to 'name' in 'products_stg'.
    sku: mapped to 'sku' in 'products_stg'.
    description: mapped to 'description' in 'products_stg'.
    md5: mapped to 'md5' in 'products_stg'.
    product: mapped to 'product' in 'products_stg'.
    
    CREATE TABLE products (
                 name varchar(255) ,
                 sku varchar(255) NOT NULL,
                 description varchar(255) NOT NULL,
                 md5 uuid NOT NULL,
                 product varchar(255),
                 PRIMARY KEY (sku, description)
                );
