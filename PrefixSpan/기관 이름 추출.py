import numpy as np
import pandas as pd
import json
from pandas import json_normalize

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

new_df = pd.DataFrame()
for i in range(0,len(data)):
    s_data = search_data.iloc[i]
    dict_sd = s_data.replace("'", "\"")
    json_string = json.loads(dict_sd)
    json_df = json_normalize(json_string)
    new_df = pd.concat([new_df,json_df],ignore_index=True)
inst_nm = new_df[['ATT_INST_NM']]
print(inst_nm.unique())
# 기관 이름 추출해 내기.

