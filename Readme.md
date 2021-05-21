# Data Qna Demo

This is a simple BigQuery DataQna demo that showcases the power of natural language query on BigQuery tables.

## Requirements

* Save your service account credentials json file under **secrets** folder. Make sure your service account has all the required permissions to execute queries on BigQuery.
* In **config.py** under **src** folder, enter your **project_name** and enter the tables you want to query within **tables_list** variable. Enter the BigQuery tables in the format **'dataset_name.table_name'** separated by commas. For example **['lab.iowa_liquor_sales','lab.chicago_taxi_trips']**
* Make sure you have docker installed on your machine. While in the root directory of this project, type `docker-compose up` to build the docker container.
* Type `http://localhost:8501/` on your browser to start interacting with the demo

##Screenshot

![alt text](Data_qna_demo_image.png?raw=true)