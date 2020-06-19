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
      1)name: mapped to 'name' in csv file.
      2)sku: mapped to 'sku' in csv file.
      3)description: mapped to 'description' in csv file.
      4)md5: an md5 hashcode created in script on 'sku' and 'description' (which was the unique combination) to create a unique code for              each unique value. This column is used for joining the staging and target tables during the update/insert process as it
             less in size and is always unique based on th condition.
      5)product: copy of the 'sku' column, as 'sku' is part of the PK, this column would be used for updates.

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
      1)name: mapped to 'name' in 'products_stg'.
      2)sku: mapped to 'sku' in 'products_stg'.
      3)description: mapped to 'description' in 'products_stg'.
      4)md5: mapped to 'md5' in 'products_stg'.
      5)product: mapped to 'product' in 'products_stg'.

      CREATE TABLE products (
                   name varchar(255) ,
                   sku varchar(255) NOT NULL,
                   description varchar(255) NOT NULL,
                   md5 uuid NOT NULL,
                   product varchar(255),
                   PRIMARY KEY (sku, description)
                  );

  'products_agg':
    This is the aggregate table which uses 'products' table as input to create a count of products by name.

    Column Details:
      1)name: takes the 'name' column from 'products' as data input
      2)number_of_products: takes the count of 'product' column in 'products' table and groups by 'name'.

    CREATE TABLE products_agg (
                 name varchar(255) ,
                 number_of_products int
                 );
                 
    Sample Data:
      ![image](https://user-images.githubusercontent.com/18376158/85153975-79f0dc00-b274-11ea-9121-c466efeaec98.png)
      https://user-images.githubusercontent.com/18376158/85153975-79f0dc00-b274-11ea-9121-c466efeaec98.png
    
    
    
What was done from Points to Achieve:
  1) Implemented concepts of OOPS:
      Different functions are defined for each operation (eg. truncate table, bulk load, inser/update) and they are called in main.
      
  2) Support regular non-blocking parallel ingestion for scale:
      a) This program uses the ,multiprocessing' class in python, which i used to chunk the csv file into equal pieces and give input to          each core of the processor which would bulk load it into the staging table simultaneously, thus reducing ingestion time. The            program also dynamically finds out the number of cores on a cpu using 'mp.cpu_count()'.
      b) Also, for scale, I used a column 'md5' that stores md5 hash of the PK, it is much lower in size due to the datatype 'uuid' and          thus results in faster joins.
      
   3) All product details in a single table 'products'. The 'products_stg' is used as an intermediate to use ELT principle which is           found useful for large data.
   
   4) Aggregated table named 'products_agg' created with required columns.


What would I do to improve if given more days:

  1) Figure out a way/condition to disect the data in staging and insert them parallely into target. I tried using the process_id as a        column based on the number of subprocesses, but insertion in the target table simulataneously was causing a lock and multiplying        insertion time.
  
  2) Create a unique numeric column based on the PK and use it as the join codition because 'int' datatype takes only 4 bytes in              postgresql. I tried, but due mutiprocessing the chunks, a value in each chunk had an id matching to a value in another chunk.
