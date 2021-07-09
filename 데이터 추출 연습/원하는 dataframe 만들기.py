import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np
import json
from pandas import json_normalize


rc('font', family='AppleGothic')
plt.rcParams['axes.unicode_minus'] = False  #plot에서 한글 깨지는걸 해결.

data = pd.read_csv("ts_data_accident-2020.csv", low_memory=False)
pd.set_option('display.max_columns',None)   # columns 항목이 굉장히 길어도 생략안하고 끝까지 출력하게 해주는 코드.

# 정확한 방법인지는 확인이 안되지만, 먼저 dataframe을 만들어서 하나를 추가해놓고 계속 추가하는 방식.
risk_df = pd.DataFrame()

data_size = 200 # 원하는 데이터 사이즈. 최댓값은 len(data)로 해야 한다.
for i in range(0,data_size):
    v2 = data['RISK_V2'].iloc[i]
    dict_v2 = v2.replace("'", "\"")
    json_string = json.loads(dict_v2)
    json_df = json_normalize(json_string)
    risk_df = pd.concat([risk_df,json_df],ignore_index=True)    #DataFrame 합쳐주기. ignore_index = True를 해야 index가 재구성 된다.

#   // 지금은 안쓸거니까 .risk_df = risk_df.reindex(sorted(risk_df.columns),axis=1)   # 보기 편하게, columns name을 정렬한다.

new_df = risk_df[['ASSETS_VAL_6','ASSETS_VAL_7','ASSETS_VAL_8','ASSETS_VAL_9','ASSETS_VAL_10']]
new_df = pd.concat([data['TW_DMG_PORT'].head(data_size),new_df],axis=1) # 이건 열 합쳐주기. axis = 1 이면 열 합치는 것.
print(new_df.describe())

# 포트번호당 공격 횟수

portnum = {}

for port in data['TW_DMG_PORT'] :   # 포트 번호당 공격횟수를 나타내는 딕셔너리.
    portfind = False
    port = str(port)
    for num in portnum.keys():
        if port == num:
            portnum[port] += 1
            portfind = True

    if not portfind:
        portnum[port] = 1

port_df = pd.DataFrame(portnum,index=['Count'])
print(port_df.sort_values(ascending = False, by = 'Count', axis=1).to_markdown())