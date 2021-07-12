import pandas as pd
from dataprep.eda import plot, plot_correlation, plot_missing   # dataprep.eda의 plot사용. 보기 훨씬 깔끔하다.
import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np
import json
from pandas import json_normalize
from mlxtend.preprocessing import TransactionEncoder        # apriori 사용하려고 추가하는 모듈들.
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules


rc('font', family='AppleGothic')
plt.rcParams['axes.unicode_minus'] = False  # matplotlib.pyplot에서 한글 깨지는걸 해결.

data = pd.read_csv("ts_data_accident-2020.csv", low_memory=False)
pd.set_option('display.max_columns',None)   # columns 항목이 굉장히 길어도 생략안하고 끝까지 출력하게 해주는 코드.

# 정확한 방법인지는 확인이 안되지만, 먼저 dataframe을 만들어서 하나를 추가해놓고 계속 추가하는 방식.
risk_df = pd.DataFrame()

data_size = len(data) # 원하는 데이터 사이즈. 최댓값은 len(data)로 해야 한다.
for i in range(0,data_size):
    v2 = data['RISK_V2'].iloc[i]
    dict_v2 = v2.replace("'", "\"")
    json_string = json.loads(dict_v2)
    json_df = json_normalize(json_string)
    risk_df = pd.concat([risk_df,json_df],ignore_index=True)    #DataFrame 합쳐주기. ignore_index = True를 해야 index가 재구성 된다.

#   // 지금은 안쓸거니까 .risk_df = risk_df.reindex(sorted(risk_df.columns),axis=1)   # 보기 편하게, columns name을 정렬한다.

new_df = risk_df[['ASSETS_VAL_6','ASSETS_VAL_7','ASSETS_VAL_8','ASSETS_VAL_9','ASSETS_VAL_10']]
new_df = pd.concat([data['TW_DMG_PORT'].head(data_size),new_df],axis=1) # 이건 열 합쳐주기. axis = 1 이면 열 합치는 것.

# 공격 포트의 넘버가 80번인 개수가 21224로 제일 많았다. 그래서 80번 포트 안에서 VAL들의 상관관계를 살펴 보기로 했다.
# 계획 : 포트 80인것들의 value를 다 저장해서 놔두고, 이걸 apriori에 돌리려고 한다.

#### apriori를 사용하기 위해 데이터셋으로 만들어줘야 하는데, 인덱싱 for문과 인덱싱은 엄청나게 오래 걸린다. 고로 groubby와 join을 사용해보자.
# 일단 생각은, DataSet으로 만들건데, val_6~10마다 구분을 해야 하므로, 아예 데이터셋에 ['val_6:10','val_7:10'] 이런식으로 통일해서 통 문자열로 넣으려고 한다.
# ['달걀','계란'] 넣는거랑 다를 게 없다. 상품명 처럼 사용하려고 한다. 그럼 먼저 데이터를 가공해보자.
# 원래 numpy로 넘기면 배열로 쭉 나오는데, 그럼 숫자가 중복된 것도 체크가 되어 버린다.

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
te_result = te.fit(dataset).transform(dataset)
df = pd.DataFrame(te_result, columns=te.columns_) #위에서 나온걸 보기 좋게 데이터프레임으로 변경
frequent_itemsets = apriori(df, min_support=0.5, use_colnames=True)
frequent_itemsets