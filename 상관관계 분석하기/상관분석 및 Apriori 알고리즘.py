import pandas as pd
from mlxtend.preprocessing import TransactionEncoder        # apriori 사용하려고 추가하는 모듈들.
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules
import json
from pandas import json_normalize

data = pd.read_csv("../ts_data_accident-2020.csv", low_memory=False)
pd.set_option('display.max_columns',None)

# 정확한 방법인지는 확인이 안되지만, 먼저 dataframe을 만들어서 하나를 추가해놓고 계속 추가하는 방식.
risk_df = pd.DataFrame()

data_size = len(data) # 원하는 데이터 사이즈. 최댓값은 len(data)로 해야 한다. 이거 하나로 새로운 dataframe size 수정 다 가능.

for i in range(0,data_size):
    v2 = data['RISK_V2'].iloc[i]
    dict_v2 = v2.replace("'", "\"")
    json_string = json.loads(dict_v2)
    json_df = json_normalize(json_string)
    risk_df = pd.concat([risk_df,json_df],ignore_index=True)    #DataFrame 합쳐주기. ignore_index = True를 해야 index가 재구성 된다.

#   // 지금은 안쓸거니까 .risk_df = risk_df.reindex(sorted(risk_df.columns),axis=1)   # 보기 편하게, columns name을 정렬한다.

new_df = risk_df[['ASSETS_VAL_6','ASSETS_VAL_7','ASSETS_VAL_8','ASSETS_VAL_9','ASSETS_VAL_10']]
new_df = pd.concat([data['TW_DMG_PORT'].head(data_size),new_df],axis=1) # 이건 열 합쳐주기. axis = 1 이면 열 합치는 것.

dataset = []
port80_df = new_df.groupby('TW_DMG_PORT').get_group(80) # TW_DMG_PORT = 80 인 데이터들.
port80_df.drop(['TW_DMG_PORT'], axis = 1)# Port80인거 아니까 이 열 필요없음.
clist = port80_df.columns.values.tolist()   # 그 데이터들의 columne들.
for i in range(0,200):
    str_list = []
    val = port80_df.iloc[i]
    for j in range(0,len(clist)):
        new_str = str(clist[j]) + " : " + str(val[clist[j]])
        str_list.append(new_str)
    dataset.append(str_list)

# 수작업으로 데이터셋 만들기..
te = TransactionEncoder()
te_result = te.fit(dataset).transform(dataset)  # 데이터셋들을 true false로 분석.
df = pd.DataFrame(te_result, columns=te.columns_) #위에서 나온걸 데이터프레임으로 변경
frequent_itemsets = apriori(df, min_support=0.5, use_colnames=True) # apriori 적용.
association_rules(frequent_itemsets, metric="confidence", min_threshold=0.3) # 이걸 다시 상관 분석으로.

## a priori 적용 과정.