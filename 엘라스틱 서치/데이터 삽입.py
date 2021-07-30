from elasticsearch import Elasticsearch
from elasticsearch import helpers
es = Elasticsearch('localhost:9200')
es.info()

# ========= 원본 데이터 ==========
edict = elasticdf.to_dict('records')
for i in range(0, len(elasticdf)):
    # 'TW_DMG_PORT','ASSETS_VAL_6','ASSETS_VAL_7','ASSETS_VAL_8','ASSETS_VAL_9','ASSETS_VAL_10','ACCD_ACCEPT_DT'
    docs = {
        'TW_DMG_PORT': edict[i]['TW_DMG_PORT'],
        'ASSETS_VAL_6': edict[i]['ASSETS_VAL_6'],
        'ASSETS_VAL_7': edict[i]['ASSETS_VAL_7'],
        'ASSETS_VAL_8': edict[i]['ASSETS_VAL_8'],
        'ASSETS_VAL_9': edict[i]['ASSETS_VAL_9'],
        'ASSETS_VAL_10': edict[i]['ASSETS_VAL_10'],
        'ACCD_ACCEPT_DT': edict[i]['ACCD_ACCEPT_DT']
    }
    res = es.index(index='original', doc_type='_doc', body=docs)

# ======= 근데 이게 원본 데이터가 너무 많아서, bulk로 처리해보자.


# ==========상관관계 분석 데이터 ============
ndict = real_df.to_dict('records')  # 딕셔너리로 만들어준다.
for i in range(0, len(real_df)):
    docs = {
        'antecedents': ndict[i]['antecedents'],
        'consequents': ndict[i]['consequents'],
        'support': round(ndict[i]['support'], 7),
        'confidence': round(ndict[i]['confidence'], 7),
        'leverage': round(ndict[i]['leverage'], 7),
        'lift': round(ndict[i]['lift'], 7)
    }
    res = es.index(index='as_rule', doc_type="_doc", body=docs)


