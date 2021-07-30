import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np
import json
from pandas import json_normalize
from dataprep.eda import plot, plot_correlation, plot_missing
from mlxtend.preprocessing import TransactionEncoder        # apriori 사용하려고 추가하는 모듈들.
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules
from elasticsearch import Elasticsearch
from elasticsearch import helpers

data = pd.read_csv("ts_data_accident-2020.csv", low_memory=False)
pd.set_option("display.max_rows", None, "display.max_columns", None)
MAX_size = len(data) # 원하는 데이터 사이즈. 최댓값은 len(data)로 해야 한다.


def makedataframe(data_len):
    risk_df = pd.DataFrame()
    for i in range(0, data_len):
        v2 = data['RISK_V2'].iloc[i]
        dict_v2 = v2.replace("'", "\"")
        json_string = json.loads(dict_v2)
        json_df = json_normalize(json_string)
        risk_df = pd.concat([risk_df, json_df],
                            ignore_index=True)  # DataFrame 합쳐주기. ignore_index = True를 해야 index가 재구성 된다.
    rtr_df = risk_df[['ASSETS_VAL_6', 'ASSETS_VAL_7', 'ASSETS_VAL_8', 'ASSETS_VAL_9', 'ASSETS_VAL_10']]
    rtr_df = pd.concat([data['TW_DMG_PORT'].head(data_len), rtr_df], axis=1)  # 이건 열 합쳐주기. axis = 1 이면 열 합치는 것.
    #  지금은 안쓸건데, risk_df = risk_df.reindex(sorted(risk_df.columns),axis=1)   # 보기 편하게, columns name을 정렬한다.
    return rtr_df  # 어차피 가공한 데이터프레임인 new_df만 사용할 거니까 이걸 반환값으로 하면 간편하겠지?


# ======================= 데이터프레임을 상관관계분석을 위한 DataSet으로 만들어주는 함수. =================================
def makedataset(data_size):  # 함수화 해서 간편하게 하자. range: 0부터 몇 번째 범위까지 데이터셋을 만들것인지 정해주자.
    new_df = makedataframe(data_size)
    column_list = new_df.columns.values.tolist()  # 그 데이터들의 columne들. TW_DMG_PORT, ASSETS_VAL_6~10.
    ret_dataSet = []
    # ==== 엘라스틱 서치에 분석에 사용된 원래 데이터를 넣어주기 위해서 데이터프레임을 하나 더 만들어준다.
    cop_df = new_df.copy()  # 깊은 복사.
    cop_df = pd.concat([cop_df, data['ACCD_ACCEPT_DT'].head(data_size)], axis=1)  # 시간이 중요하니까 DT까지 넣어주자.
    ret_df = pd.DataFrame(
        columns=['TW_DMG_PORT', 'ASSETS_VAL_6', 'ASSETS_VAL_7', 'ASSETS_VAL_8', 'ASSETS_VAL_9', 'ASSETS_VAL_10',
                 'ACCD_ACCEPT_DT'])
    for idx in range(0, data_size):  # 함수의 요소값은 range 까지.
        str_list = []
        val = new_df.iloc[idx]
        copiloc_df = cop_df.iloc[[idx]]
        for j in range(0, len(column_list)):
            data_name = column_list[j]
            data_val = val[column_list[j]]
            if data_val == 0:  # 0이면 데이터셋에 추가하지 말자.
                continue
            new_str = data_name + " : " + str(data_val)
            str_list.append(new_str)

        if len(str_list) <= 1:  # 1이면 포트번호밖에 없는 거다. 포트번호밖에 없는 데이터셋은 의미도 없고 support값에 혼란을 주기 때문에 걸러줘야함.
            continue

        ret_dataSet.append(str_list)
        ret_df = pd.concat([ret_df, copiloc_df], ignore_index=True)

    return ret_dataSet, ret_df

dataset, elasticdf = makedataset(MAX_size)
print(elasticdf)
# dataset : 상관 분석을 위한 데이터 셋, elasticdf : 엘라스틱서치에 넣기 위한 데이터.

# =============================== 상관관계 분석 적용 ============================
te = TransactionEncoder()
te_result = te.fit(dataset).transform(dataset)
df = pd.DataFrame(te_result, columns=te.columns_) #위에서 나온걸 데이터프레임으로 변경
frequent_itemsets = apriori(df, min_support=0.00001, use_colnames=True)
assorule_df = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.00001) # 이걸 다시 상관 분석으로.
real_df = pd.DataFrame()
for i in range(0,len(assorule_df)):
    temp_df = assorule_df.iloc[i]
    check_list = list(temp_df['antecedents'])
    check_list = sorted(check_list,reverse=True)
    if check_list[0].find('TW_DMG_PORT') == -1: # 못찾으면.
        continue
    temp_df = pd.DataFrame(temp_df).T
    temp_df = temp_df.drop(['antecedent support','consequent support'],axis = 1)
    real_df = pd.concat([real_df, temp_df], ignore_index = True)

real_df = real_df.sort_values('support', ascending=False)
real_df = real_df.reset_index(drop=True) # 정렬 후 인덱스 초기화.
real_df["antecedents"] = real_df["antecedents"].apply(lambda x: ', '.join(list(x))).astype("unicode")  #frozenset to string
real_df["consequents"] = real_df["consequents"].apply(lambda x: ', '.join(list(x))).astype("unicode")

# ======= 엘라스틱서치에 데이터 삽입하는 구간. 먼저 결과 값 데이터.
es = Elasticsearch('localhost:9200')
es.info()
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
    res = es.index(index='as_rule', doc_type="result", body=docs)
