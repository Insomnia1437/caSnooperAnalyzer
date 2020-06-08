# -*- coding: utf-8 -*-
# @Time    : 2020-06-08
# @File    : esConnector
# @Software: PyCharm
# @Author  : Di Wang(KEK Linac)
# @Email   : sdcswd@gmail.com
from elasticsearch import Elasticsearch


class ESConnector:
    def __init__(self, url):
        self.es = Elasticsearch([url])

    def es_ok(self):
        return self.es.ping()

    def index_exist(self, index):
        if self.es.indices.exists(index):
            print('Info: index exists! %s' % index)
            return True
        return False

    def index_search(self, index):
        if self.index_exist(index):
            body = {
                "size": 10000,
                "query": {
                    "bool": {
                        "filter": [
                            {
                                "range": {
                                    "Hz": {"gte": 1}
                                }
                            }
                        ]
                    },
                }
            }
            response = self.es.search(index=index, body=body)
            if response['_shards']['failed'] == 0:
                return response['hits']['hits']
        return []

