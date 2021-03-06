from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_restplus import Api
from elasticsearch import Elasticsearch, TransportError
from werkzeug.contrib.fixers import ProxyFix
from gensim.models.keyedvectors import KeyedVectors
from .lib.docsim import DocSim
import json
import os.path
from .config import config_by_name

db = SQLAlchemy()
flask_bcrypt = Bcrypt()

# Load corpus
ds = None
model_path = './data/model.txt'
if os.path.isfile(model_path):
  stopwords_path = './data/stopwords-en.txt'
  model = KeyedVectors.load_word2vec_format(model_path)
  with open(stopwords_path, 'r') as fh:
    stopwords = fh.read().split(',')
  ds = DocSim(model, stopwords=stopwords)

def create_app(config_name):
  app = Flask(__name__)
  app.config.from_object(config_by_name[config_name])
  app.wsgi_app = ProxyFix(app.wsgi_app)

  if config_name == 'prod':
    @property
    def specs_url(self):
      return url_for(self.endpoint('specs'), _external=True, _scheme='https')
    Api.specs_url = specs_url

  db.init_app(app)
  flask_bcrypt.init_app(app)

  # Create ES index.
  es = Elasticsearch(app.config['ELASTICSEARCH_URL'])
  for key in ['ELASTICSEARCH_GLOSSARY', 'ELASTICSEARCH_SIMILARITY']:
    try:
      es.indices.create(index=app.config[key])
    except TransportError as e:
      # ignore already existing index
      if e.error == 'resource_already_exists_exception':
        pass
      else:
        raise
  es.indices.put_mapping(
    doc_type='_doc',
    body=json.load(open('./elasticsearch/alegre_glossary.json')),
    index=app.config['ELASTICSEARCH_GLOSSARY']
  )
  es.indices.close(index=app.config['ELASTICSEARCH_SIMILARITY'])
  es.indices.put_settings(
    body=json.load(open('./elasticsearch/alegre_similarity_settings.json')),
    index=app.config['ELASTICSEARCH_SIMILARITY']
  )
  es.indices.open(index=app.config['ELASTICSEARCH_SIMILARITY'])
  es.indices.put_mapping(
    doc_type='_doc',
    body=json.load(open('./elasticsearch/alegre_similarity.json')),
    index=app.config['ELASTICSEARCH_SIMILARITY']
  )

  return app
