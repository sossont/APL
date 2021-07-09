import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np

rc('font', family='AppleGothic')
plt.rcParams['axes.unicode_minus'] = False  #plot에서 한글 깨지는걸 해결.

data = pd.read_csv("ts_data_accident-2020.csv", low_memory=False)
pd.set_option('display.max_columns',None)   # columns 항목이 굉장히 길어도 생략안하고 끝까지 출력하게 해주는 코드.

portnumhead = {}    # dictionary.
portnumtail = {}

for port in data['TW_DMG_PORT'].head(50) :   # 포트 번호당 공격횟수를 나타내는 딕셔너리.
    portfind = False
    port = str(port)
    for num in portnumhead.keys():
        if port == num:
            portnumhead[port] += 1
            portfind = True

    if not portfind:
        portnumhead[port] = 1

sorts = sorted(portnumhead.items())
num, count = zip(*sorts)
Index = np.arange(len(sorts))
plt.bar(Index,count)
plt.xticks(Index,num)
plt.xlabel('포트 번호',fontsize=15)
plt.ylabel('공격 횟수',fontsize=15)
plt.savefig('./head.png')

for port in data['TW_DMG_PORT'].tail(50) :   # 포트 번호당 공격횟수를 나타내는 딕셔너리.
    portfind = False
    port = str(port)
    for num in portnumtail.keys():
        if port == num:
            portnumtail[port] += 1
            portfind = True

    if not portfind:
        portnumtail[port] = 1

sorts = sorted(portnumtail.items())
num, count = zip(*sorts)
Index = np.arange(len(sorts))
plt.bar(Index,count)
plt.xticks(Index,num)
plt.xlabel('포트 번호',fontsize=15)
plt.ylabel('공격 횟수',fontsize=15)
plt.savefig('./tale.png')