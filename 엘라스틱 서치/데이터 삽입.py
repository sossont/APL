from elasticsearch import Elasticsearch
from elasticsearch import helpers

es = Elasticsearch()
es.info()

data = [    # 삽입할 데이터. 예시로 조건절, 결과절, support 3값만 넣어두었다. id는 인덱스를 넣어줌.
    {
        "_index": "as_rule",
        "_type": "object",
        "_id": x[3],
        "_source": {
            "antecedents": x[0],
            "consequents": x[1],
            "support": x[2]
        }
    }
    for x in zip(real_df['antecedents'],real_df['consequents'],real_df['support'],real_df.index)
]
helpers.bulk(es, data)