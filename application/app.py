"""
web application backend code for querying elastic search.
"""


from flask import Flask, request, render_template, redirect, url_for
from elasticsearch import Elasticsearch

app = Flask(__name__)

# Configure Elasticsearch connection
es = Elasticsearch(['http://localhost:9200'])


@app.route('/', methods=['GET', 'POST'])
def index ():
    results = []
    error = None
    page = int(request.args.get('page', 1))

    # set initial result per page.
    size = 100

    start = (page - 1) * size

    if request.method == 'POST':
        user_id = request.form.get('userId')
        movie_id = request.form.get('movieId')

        if not user_id and not movie_id:
            error = "Please enter either a User ID or a Movie ID."
        else:
            return redirect(url_for('index', userId=user_id, movieId=movie_id, page=1))

    user_id = request.args.get('userId')
    movie_id = request.args.get('movieId')

    if user_id or movie_id:
        # Build query
        query = {
            "bool": {
                "must": []
            }
        }
        if user_id:
            query["bool"]["must"].append({"match": {"userId": user_id}})
        if movie_id:
            query["bool"]["must"].append({"match": {"movieId": movie_id}})

        # Query Elasticsearch
        response = es.search(index="your_index_name", body={"query": query, "from": start, "size": size})
        results = response['hits']['hits']
        total_results = response['hits']['total']['value']
    else:
        total_results = 0

    return render_template('index.html', results=results, error=error, page=page, size=size,
                           total_results=total_results, user_id=user_id, movie_id=movie_id)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
