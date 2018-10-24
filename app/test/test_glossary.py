import unittest
import json
from elasticsearch import helpers, Elasticsearch, TransportError
from flask import current_app as app

from app.main import db
from app.test.base import BaseTestCase

class TestGlossaryBlueprint(BaseTestCase):
    maxDiff = None

    def setUp(self):
      es = Elasticsearch(app.config['ELASTICSEARCH_URL'])
      es.indices.delete(index=app.config['ELASTICSEARCH_GLOSSARY'])
      es.indices.create(index=app.config['ELASTICSEARCH_GLOSSARY'])
      es.indices.put_mapping(
        doc_type='_doc',
        body=json.load(open('./elasticsearch/alegre_glossary.json')),
        index=app.config['ELASTICSEARCH_GLOSSARY']
      )

    def test_glossary_mapping(self):
      es = Elasticsearch(app.config['ELASTICSEARCH_URL'])
      mapping = es.indices.get_mapping(
        doc_type='_doc',
        index=app.config['ELASTICSEARCH_GLOSSARY']
      )
      self.assertDictEqual(
        mapping[app.config['ELASTICSEARCH_GLOSSARY']]['mappings']['_doc'],
        json.load(open('./elasticsearch/alegre_glossary.json'))
      )

    def test_glossary_queries(self):
      es = Elasticsearch(app.config['ELASTICSEARCH_URL'])
      success, _ = helpers.bulk(es,
        json.load(open('./app/test/data/glossary.json')),
        index=app.config['ELASTICSEARCH_GLOSSARY']
      )
      self.assertTrue(success)
      es.indices.refresh(index=app.config['ELASTICSEARCH_GLOSSARY'])
      result = es.search(
        doc_type='_doc',
        index=app.config['ELASTICSEARCH_GLOSSARY'],
        body={
          "query": {
            "simple_query_string": {
              "fields": [ "en" ],
              "query": "talking"
            }
          }
        }
      )
      self.assertEqual("Por que minha mãe conversa com a TV?", result['hits']['hits'][0]['_source']['pt'])
      result = es.search(
        doc_type='_doc',
        index=app.config['ELASTICSEARCH_GLOSSARY'],
        body={
          "_source": ["pt"],
          "query": {
            "bool": {
              "must": [
                {
                  "match_phrase": { "en": "mothers talking" }
                },
                {
                  "nested": {
                    "path": "context",
                    "query": {
                      "bool": {
                        "must": [
                          {
                            "match": {
                              "context.user": "ccx"
                            }
                          }
                        ]
                      }
                    }
                  }
                }
              ],
              "filter": [
                { "exists": { "field": "pt" } }
              ]
            }
          }
        }
      )
      self.assertEqual("Por que minha mãe conversa com a TV?", result['hits']['hits'][0]['_source']['pt'])


if __name__ == '__main__':
    unittest.main()