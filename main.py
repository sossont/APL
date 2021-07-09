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

print(pd.DataFrame(portnum,index=['Count']))
