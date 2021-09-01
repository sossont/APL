import pandas as pd
import json
from pandas import json_normalize
from prefixspan import PrefixSpan

data = pd.read_csv("ts_data_accident-2020_sample.csv", low_memory=False)
pd.set_option('display.max_columns',None)


####### Data 11가지 갖고 있어야 한다.

search_data = data['TW_ATT_IP_SEARCH_DATA'] # 1. 기관이름
att_type_code = data['DRULE_ATT_TYPE_CODE1']    # 2.공격 code
risk_V2 = data['RISK_V2']   # 3.자산, 9. 자산 안에 의도 7개도 들어있음.
att_ip = data['TW_ATT_IP']  # 4.위협 공격 IP
dmg_ip = data['TW_DMG_IP']  # 5.위협 피해 IP
att_port = data['TW_ATT_PORT']  # 6. 위협 공격 PORT
dmg_port = data['TW_DMG_PORT']  # 7. 위협 피해 PORT
att_ct_code = data['TW_ATT_CT_CODE']    # 8. 공격국가 코드

#### 기관이름 추출하기 위해 작업.
new_df = pd.DataFrame()
for i in range(0,len(data)):
    s_data = search_data.iloc[i]
    dict_sd = s_data.replace("'", "\"")
    json_string = json.loads(dict_sd)
    json_df = json_normalize(json_string)
    new_df = pd.concat([new_df,json_df],ignore_index=True)


av_df = pd.DataFrame()
for i in range(0, len(data)):
    v_data = risk_V2.iloc[i]
    dict_v2 = v_data.replace("'", "\"")
    json_string = json.loads(dict_v2)
    json_df = json_normalize(json_string)
    av_df = pd.concat([av_df, json_df], ignore_index=True)

    # 먼저 json형식으로 처리해서 자산들 다 DataFrame 항목으로 만들기.

print(av_df)  # av_df : risk_V2안에 들어가있는 모든 항목들을 dataframe화 시킨 것.


## prefix_str : 최종 데이터셋.

prefix_str = []  # PrefixSpan에 집어넣을 배열이다.

for i in range(0, len(data)):
    sample_df = av_df.iloc[i]
    arr_str = []

    inst_name = new_df.iloc[i]['ATT_INST_NM']  # 기관 이름 삽입
    arr_str.append(inst_name)
    # 나머지 다 삽입. 총 8개 데이터.
    arr_str.extend([att_ip[i], dmg_ip[i], att_port[i], dmg_port[i], att_ct_code[i]])

    # 자산 넣는 부분.
    for j in range(1, 23):  # 1부터 22번까지 있으니까.
        val_str = "ASSETS_VAL_"
        val_str += str(j)
        num = sample_df[val_str]
        if num != 0:  # 0이 아닌 것들만 살려두자.
            val_str = val_str + ":" + str(num)
            arr_str.append(val_str)

    # 여기는 의도 넣는 부분.
    for j in range(0, 7):  # 0부터 6번까지 있다.
        int_str = "INTENT_VAL_"
        int_str += str(j)
        num = sample_df[int_str]
        if num != 0:
            val_str = val_str + ":" + str(num)
            arr_str.append(val_str)

    prefix_str.append(arr_str)

print(prefix_str)

### prefixspan algorithm 사용
ps = PrefixSpan(prefix_str)
print(ps.topk(5,closed=True))   # 상위 5개 출현 빈도

### 수정한 코드

prefix_list = []
for i in range(0,len(data)):
    ll = []
    new_str = ' '.join(str(e) for e in prefix_str[i])
    ll.append(new_str)
    ll.append(att_type_code[i])
    prefix_list.append(ll)

ps = PrefixSpan(prefix_list)
result = ps.topk(5,closed=True)
answer = []
for items in result:
    ans_list = []
    freq = items[0]
    str1 = items[1][0]
    nlist = str1.split(' ')
    str2 = items[1][1]
    ans_list.extend((nlist,[str2],freq))
    answer.append(ans_list)
print(answer)