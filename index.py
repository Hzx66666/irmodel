import re
import json
import time

from elasticsearch import Elasticsearch
from elasticsearch import helpers
from elasticsearch_dsl import Index, Document, Text, Keyword, Integer
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import tokenizer, analyzer
from elasticsearch_dsl.query import MultiMatch, Match
from elasticsearch_dsl import Search

# Connect to local host server
connections.create_connection(hosts=['127.0.0.1'])

# Create elasticsearch object
es = Elasticsearch()

# Define analyzers appropriate for your data.
# You can create a custom analyzer by choosing among elasticsearch options
# or writing your own functions.
# Elasticsearch also has default analyzers that might be appropriate.
my_analyzer = analyzer('custom', tokenizer='whitespace',
                       filter=[])


# --- Add more analyzers here ---
# use stopwords... or not?
# use stemming... or not?

# Define document mapping (schema) by defining a class as a subclass of Document.
# This defines fields and their properties (type and analysis applied).
# You can use existing es analyzers or use ones you define yourself as above.

class Movie(Document):
    text = Text(analyzer=my_analyzer)
    raw = Text(analyzer=my_analyzer)
    ptext = Text(analyzer=my_analyzer)
    # --- Add more fields here ---
    # What data type for your field? List?
    # Which analyzer makes sense for each field?

    # override the Document save method to include subclass field definitions
    def save(self, *args, **kwargs):
        return super(Movie, self).save(*args, **kwargs)


def create_index(es_object, index_name='sample_film_index'):
    created = False
    # index settings

    settings = {
        "mappings": {
            "properties": {
                "text": {
                    "type": "text",
                    "analyzer": "whitespace",
                    "search_analyzer": "whitespace"
                },
                "raw": {
                    "type": "text",
                    "analyzer": "whitespace",
                    "search_analyzer": "whitespace"
                },
                "ptext": {
                    "type": "text",
                    "analyzer": "whitespace",
                    "search_analyzer": "whitespace"
                }
            }
        },
    }
    try:
        if es_object.indices.exists(index=index_name):
            es_object.indices.delete(index=index_name)
        # Ignore 400 means to ignore "Index Already Exist" error.
        res = es_object.indices.create(index=index_name, body=settings)
        print(res)
        print('Created Index')
        created = True
    except Exception as ex:
        print(str(ex))
    finally:
        return created


'''
def store_record(elastic_object, index_name='sample_film_index', record='rmrb.json'):
    try:
        # Open the json film corpus
        with open(record, 'r', encoding='utf-8') as data_file:
            # load movies from json file into dictionary
            movies = json.load(data_file)
            size = len(movies)

        # Action series for bulk loading with helpers.bulk function.
        # Implemented as a generator, to return one movie with each call.
        # Note that we include the index name here.
        # The Document type is always 'doc'.
        # Every item to be indexed must have a unique key.
        def actions():
            # mid is movie id (used as key into movies dictionary)
            for mid in range(1, size + 1):
                yield {
                    "_index": index_name,
                    "_type": 'doc',
                    "_id": mid,
                    "text": movies[str(mid)]['tokens'],
                    "raw": movies[str(mid)]['text'],
                }

        helpers.bulk(elastic_object, actions())
        # outcome = elastic_object.index(index=index_name, doc_type='movie', body=record)
    except Exception as ex:
        print('Error in indexing data')
        print(str(ex))

'''


def parse_runtime(time):
    if type(time) == int:
        return time
    else:
        return None


# Populate the index
def buildIndex():
    """
    buildIndex creates a new film index, deleting any existing index of
    the same name.
    It loads a json file containing the movie corpus and does bulk loading
    using a generator function.
    """
    film_index = Index('sample_film_index')

    # film_index.settings(index={'mapping': {'ignore_malformed': True}})
    if film_index.exists():
        film_index.delete()  # Overwrite any previous version
    # film_index.document(Movie)

    create_index(es)
    # Open the json film corpus
    with open('rmrb.json', 'r', encoding='utf-8') as data_file:
        # load movies from json file into dictionary
        movies = json.load(data_file)
        size = len(movies)
    # Action series for bulk loading with helpers.bulk function.
    # Implemented as a generator, to return one movie with each call.
    # Note that we include the index name here.
    # The Document type is always 'doc'.
    # Every item to be indexed must have a unique key.

    def actions():
        # mid is movie id (used as key into movies dictionary)
        for mid in range(0, size):
            yield {
                "_index": "sample_film_index",
                "_id": mid,
                "_source": {
                    "text": movies[str(mid)]['tokens'],
                    "raw": movies[str(mid)]['text'],
                    "ptext": movies[str(mid)]['ptokens']
                }
            }
    helpers.bulk(es, actions())

# command line invocation builds index and prints the running time.


def main():
    start_time = time.time()
    buildIndex()
    # create_index(es)
    # store_record(es)
    print("=== Built index in %s seconds ===" % (time.time() - start_time))
    #res = es.search(index="sample_film_index", doc_type="doc")


if __name__ == '__main__':
    main()
    print(es.indices.get_mapping(index='sample_film_index'))
