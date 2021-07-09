import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import re

data = pd.read_csv("ts_data_accident-2020.csv", low_memory=False)
twdmgport = data['TW_DMG_PORT']

val6list = []
val7list = []
val8list = []
val9list = []
val10list = []

# USER_RISK_V2 항목에 있는 내가 원하는 값들을 추출한 후 데이터프레임으로 다시 만들어서 다루기 편하게 세팅해보자.
# 찾아야 하는 것들 : ASSETS_VAL_6 부터 10까지.
for riskdata in data['USER_RISK_V2']: # 'ASSETS_VAL_ 이라는 문자열을 만들어놓고 6~10 변수로 넣을 수 있는데, 이게 직관적이니까.
    riskdata = riskdata.replace(" ", "")    # 공백과 따옴표를 지워주자. 데이터 오류 방지 위해서.
    riskdata = riskdata.replace("'", "")
    val6index = re.search('ASSETS_VAL_6:\d+', riskdata).span()  # 시작 인덱스와 끝 인덱스를 받는 이유는, value가 몇 자리 인지 몰라서.
    val7index = re.search('ASSETS_VAL_7:\d+', riskdata).span()
    val8index = re.search('ASSETS_VAL_8:\d+', riskdata).span()
    val9index = re.search('ASSETS_VAL_9:\d+', riskdata).span()
    val10index = re.search('ASSETS_VAL_10:\d+', riskdata).span()
    val6 = riskdata[val6index[0] + 13 : val6index[1]]   # val6의 value 값. 7~10도 마찬가지로 해주면 된다.
    val7 = riskdata[val7index[0] + 13 : val7index[1]]
    val8 = riskdata[val8index[0]+ 13 : val8index[1]]
    val9 = riskdata[val9index[0] + 13 : val9index[1]]
    val10 = riskdata[val10index[0] + 14 : val10index[1]]  # 애는 10 이니까 위치가 하나 늘어난다.

    val6list.append(int(val6))
    val7list.append(int(val7))
    val8list.append(int(val8))
    val9list.append(int(val9))
    val10list.append(int(val10))


new_data = {'ASSETS_VAL_6' : val6list, 'ASSETS_VAL_7' : val7list, 'ASSETS_VAL_8' : val8list, 'ASSETS_VAL_9' : val9list, 'ASSETS_VAL_10' : val10list}
assets_val_df = pd.DataFrame.from_dict(new_data)

# assets_val_df 라는 새로운 데이터프레임을 만들어주었다.