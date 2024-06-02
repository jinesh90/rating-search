"""
steps:

- download from link to temp file
- extract files to local disk that mounted on docker.
-

movie lens database streaming download, unzip , data processing and inserting.
source database link is https://files.grouplens.org/datasets/movielens/ml-20m.zip
"""

from airflow import DAG
from datetime import datetime
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import zipfile
import os
import time
import pandas as pd
from elasticsearch import Elasticsearch, helpers


remote_host = "http://35.155.193.74"
remote_db_port = "9200"

dag = DAG(
    dag_id='movie_lens_data_operation',
    start_date=datetime(2024, 6, 2),
    schedule_interval=None
)


get_movies_from_imdb = BashOperator(
    task_id="download_data_from_movie_lens",
    bash_command="curl -o /tmp/ml-20m.zip -L 'https://files.grouplens.org/datasets/movielens/ml-20m.zip'",
    dag=dag
)

wait_for_sometime = BashOperator(task_id="wait_for_some_time",
                                 bash_command="sleep 5",
                                 dag=dag)


def _extract_zip_file():
    extract_path = "/tmp/data"
    if not os.path.exists(extract_path):
        os.makedirs(extract_path)
    with zipfile.ZipFile("/tmp/ml-20m.zip", 'r') as zip_ref:
        zip_ref.extractall(extract_path)


extract_movies_from_zip = PythonOperator(
    task_id="extract_movies_from_zip",
    python_callable=_extract_zip_file,
    dag=dag
)


def _csv_to_elasticsearch(file_path, index_name, chunk_size=100000, max_retries=5, retry_delay=2):
    es = Elasticsearch(
        ['{}:{}'.format(remote_host,remote_db_port)]

    )
    for df_chunk in pd.read_csv(file_path, chunksize=chunk_size):
        records = df_chunk.to_dict(orient='records')
        actions = [
            {
                "_index": index_name,
                "_source": record
            }
            for record in records
        ]

        for attempt in range(max_retries):
            try:
                helpers.bulk(es, actions)
                print("Inserted chunk of size {chunk_size}")
                break  # Break out of retry loop on success
            except (ConnectionError, Elasticsearch.exceptions.ConnectionError) as e:
                print(f"Connection error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    print(f"Failed to insert chunk after {max_retries} attempts")
                    raise
    print()


def _insert_rating_to_es():
    record_file_path = "/tmp/data/ml-20m/ml-20m/ratings.csv"
    index_name = 'rating-test'
    _csv_to_elasticsearch(record_file_path, index_name)
    print("Data inserted successfully!")


insert_data = PythonOperator(
    task_id="insert_data",
    python_callable=_insert_rating_to_es,
    dag=dag
)

# airflow dag sequence.
get_movies_from_imdb >> wait_for_sometime >> extract_movies_from_zip >> insert_data
