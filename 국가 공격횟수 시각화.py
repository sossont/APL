import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np

rc('font', family='AppleGothic')
plt.rcParams['axes.unicode_minus'] = False  #plot에서 한글 깨지는걸 해결.

data = pd.read_csv("ts_data_accident-2020.csv", low_memory=False)
pd.set_option('display.max_columns',None)   # columns 항목이 굉장히 길어도 생략안하고 끝까지 출력하게 해주는 코드.
"""
data['TW_ATT_IP'].describe()
data['TW_ATT_PORT'].describe()
data['ACCD_DMG_ATTACK_NM'].describe()
data['TW_DMG_PORT'].describe()
data['TW_DMG_IP'].describe()
data['TW_ATT_CT_NM'].describe()
data['INST_NM'].describe()
"""

country_name = set(data['TW_ATT_CT_NM'].head(50)) # 중복 제거를 위해 set 사용.
country_index = {}
for name in country_name:
    country_index[name] = 0 # 딕셔너리 생성.


for name in country_name:
    for attack in data['TW_ATT_CT_NM'].head(50):
        if name == attack:
            country_index[name] += 1

print(country_index)

sorts = sorted(country_index.items())
country,index = zip(*sorts)
Index = np.arange(len(sorts))
plt.bar(Index,index)
plt.xticks(Index,country)
plt.xlabel('국가 이름',fontsize=15)
plt.ylabel('공격 횟수',fontsize=15)
plt.show()