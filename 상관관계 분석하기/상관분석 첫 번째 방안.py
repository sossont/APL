"""
첫 번째 방법 : 모든 값을 다 넣는다.
Association Rule을 돌리기 전에 전처리 한 번, 후처리 한 번을 한다.

전처리 : 0인 값들을 무시한 데이터 셋을 추출하는데, 만약 데이터셋의 길이가 1이라면, 포트 번호만 들어온 것이 되므로, 그것도 무시해준다.
왜냐하면 포트번호만 들어가 있는 데이터셋은 support값에 혼란을 야기할 뿐, 의미 있는 데이터가 되지 못한다.

후처리 : 우리는 포트번호와 자산의 상관관계를 알고 싶기 때문에, 조건절에 포트번호가 오지 않는다면 그 값들은 다 무시한다.
왜냐하면 알고리즘 상 포트번호 말고 자산끼리의 상관관계도 분석을 하기 때문. 하지만 이 데이터들은 무시해준다.

찜찜한 부분 : 알고리즘 상 포트번호 말고 자산끼리도 분석할텐데, support 값에는 오류가 없을까?
"""

import pandas as pd
import json
from pandas import json_normalize
from mlxtend.preprocessing import TransactionEncoder        # apriori 사용하려고 추가하는 모듈들.
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules

data = pd.read_csv("ts_data_accident-2020.csv", low_memory=False)
pd.set_option('display.max_columns',None)   # columns 항목이 굉장히 길어도 생략안하고 끝까지 출력하게 해주는 코드.

MAX_size = len(data) # 원하는 데이터 사이즈. 최댓값은 len(data)로 해야 한다.

# =======================   TW_DMG_PORT랑 ASSETS_VAL_6~10 만 뽑아서 데이터프레임으로 재가공하는 함수.
# 정확한 방법인지는 확인이 안되지만, 먼저 dataframe을 만들어서 하나를 추가해놓고 계속 추가하는 방식.
def makedataframe(data_len):
    risk_df = pd.DataFrame()
    for i in range(0, data_len):
        v2 = data['RISK_V2'].iloc[i]
        dict_v2 = v2.replace("'", "\"")
        json_string = json.loads(dict_v2)
        json_df = json_normalize(json_string)
        risk_df = pd.concat([risk_df,json_df],ignore_index=True)    #DataFrame 합쳐주기. ignore_index = True를 해야 index가 재구성 된다.
    rtr_df = risk_df[['ASSETS_VAL_6','ASSETS_VAL_7','ASSETS_VAL_8','ASSETS_VAL_9','ASSETS_VAL_10']]
    rtr_df = pd.concat([data['TW_DMG_PORT'].head(data_len), rtr_df], axis=1) # 이건 열 합쳐주기. axis = 1 이면 열 합치는 것.
    #  지금은 안쓸건데, risk_df = risk_df.reindex(sorted(risk_df.columns),axis=1)   # 보기 편하게, columns name을 정렬한다.
    return rtr_df   # 어차피 가공한 데이터프레임인 new_df만 사용할 거니까 이걸 반환값으로 하면 간편하겠지?

# ======================= 데이터프레임을 상관관계분석을 위한 DataSet으로 만들어주는 함수.
def makedataset(data_size): # 함수화 해서 간편하게 하자. range: 0부터 몇 번째 범위까지 데이터셋을 만들것인지 정해주자.
    new_df = makedataframe(data_size)
    column_list = new_df.columns.values.tolist()  # 그 데이터들의 columne들. TW_DMG_PORT, ASSETS_VAL_6~10.
    ret_dataSet = []

    for index in range(0, data_size):  # 함수의 요소값은 range 까지.
        str_list = []
        val = new_df.iloc[index]
        for j in range(0, len(column_list)):
            data_name = column_list[j]
            data_val = val[column_list[j]]
            if data_val == 0:   # 0이면 데이터셋에 추가하지 말자.
                continue
            new_str = data_name + " : " + str(data_val)
            new_dict = {data_name : data_val}
            str_list.append(new_dict)

        if len(str_list) <= 1:  # 1이면 포트번호밖에 없는 거다. 포트번호밖에 없는 데이터셋은 의미도 없고 support값에 혼란을 주기 때문에 걸러줘야함.
            continue

        ret_dataSet.append(str_list)
    return ret_dataSet


dataset = makedataset(MAX_size)
te = TransactionEncoder()
te_result = te.fit(dataset).transform(dataset)
df = pd.DataFrame(te_result, columns=te.columns_)  # 위에서 나온걸 데이터프레임으로 변경
frequent_itemsets = apriori(df, min_support=0.00001, use_colnames=True)
assorule_df = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.00001)  # 이걸 다시 상관 분석으로.

# ======= Association_Rules로 나온 data값들(형식은 series)를 포트번호만 따지기위해 재가공 후 분석해준다.
real_df = pd.DataFrame()
for i in range(0, len(assorule_df)):
    temp_df = assorule_df.iloc[i]
    check_list = list(temp_df['antecedents'])
    check_list = sorted(check_list, reverse=True)
    if check_list[0].find('TW_DMG_PORT') == -1:  # 못찾으면.
        continue
    temp_df = pd.DataFrame(temp_df).T
    real_df = pd.concat([real_df, temp_df], ignore_index=True)

print(real_df)