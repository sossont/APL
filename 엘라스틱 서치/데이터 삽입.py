from elasticsearch import Elasticsearch
from elasticsearch import helpers


## conviction이 숫자값과 inf값 두 가지를 갖기 때문에 자꾸 오류가 발생한다. inf값을 먼저 처리해주어야 할 것 같다.
es = Elasticsearch()
es.info()

from elasticsearch import Elasticsearch
from elasticsearch import helpers
es = Elasticsearch('localhost:9200')
es.info()

ndict = real_df.to_dict('records') # 딕셔너리로 만들어준다.
for i in range(0,len(real_df)):
    docs = {
            'antecedents': ndict[i]['antecedents'],
            'consequents': ndict[i]['consequents'],
            'support': round(ndict[i]['support'],7),
            'confidence': round(ndict[i]['confidence'],7),
            'leverage': round(ndict[i]['leverage'],7),
            'lift': round(ndict[i]['lift'],7)
        }
    res = es.index(index='as_rule', doc_type="result",body=docs)

