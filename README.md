# rating-search
search engine for movie lens rating data with 20M ratings.

# Open source tools
- [Elasticsearch 7.17](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/index.html)
- [Apache Airflow Docker version](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html)
- [Python Flask](https://flask.palletsprojects.com/en/3.0.x)
- Amazon Web Service EC2 for hosing ES and web application ( free tier).

# Pre-requisite for running this project
- docker desktop installed and running on local machine.
- installed airflow on docker.( docker-compose.yml file given with this repo.)
- AWS/Azure account for hosting compute resources.


# How to run this project
- run DAG file (movie_lens_operation.py)
- wait for completion.( will take ~ 30-45 mins)
- go to web address (http://35.155.193.74/) where search application is running.
    - if you plan to install search application on different machine, please install requirements from requirements.txt
- search rating based on userId and/or movieId.
