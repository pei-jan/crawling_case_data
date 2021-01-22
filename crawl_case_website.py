# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 15:04:52 2021

@author: 00549879
"""

import csv , requests ,random , re , datetime
from fake_useragent import UserAgent
import pandas as pd
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
ua = UserAgent()
headers = {'User-Agent': ua.random}

company_name = []
case_name = []
announce_times = []
method = []
start_date = []
end_date = []
budget = []
remain_days = []
website = []
csv_reader = open('查詢條件設定.csv','r')
search_keys = {}
for index, line in enumerate(csv_reader.read().splitlines(),start = 1):
    search_keys[index] = line.split(',')[1]
    

url = 'https://web.pcc.gov.tw/tps/pss/tender.do?searchMode=common&searchType=basic'
patterns = { \
    '機關名稱' : '機關名稱.*?<td align="left">(.*?)&' ,
    '標案名稱' : '標案名稱.*?title="(.*?)"',
    '標案公告次數' : '<!-- 傳輸次數.*?title="(.*?)"',
    '招標方式' : '<!-- 招標方式.*?"left">(.*?)</td>',
    '公告日期' : '<!-- 公告日期.*?"left">(.*?)</td>',
    '截止日' : '<!-- 截止投標.*?"left">(.*?)</td>',
    '預算金額' : '<!-- 預算金額.*?(\d.*?)\D',
    '標案網址' : '標案名稱.*?<a href="..(.*?)" title="'
           }
data = {'isSpdt':search_keys[2],
'tenderStartDateStr':search_keys[3],
'tenderEndDateStr':search_keys[4],
'tenderStartDate':search_keys[3],
'tenderEndDate':search_keys[4],
'method':'search',
'searchMethod':True,
'tenderName':search_keys[1],
'proctrgCate':'3',
'radProctrgCate':'3',
}

session = requests.Session()
r = session.post(url, data=data,headers = headers,verify=False)
text_r = r.text.replace('\n','')
data_num = eval(re.findall('共有.*>(.*)</span>', r.text)[0])
page_turn = data_num//100

for i in range(page_turn+1):
    page = str(i+1)
    print('招標網爬取第',page,'頁')
    r = session.get('https://web.pcc.gov.tw/tps/pss/tender.do?searchMode=common&searchType=basic&method=search&isSpdt='+search_keys[2]+'&pageIndex='+page,headers = headers,verify=False)
    text_r = r.text.replace('\n','')
    company_name.extend(re.findall(patterns['機關名稱'], text_r))
    case_name.extend(re.findall(patterns['標案名稱'],text_r))
    announce_times.extend(re.findall(patterns['標案公告次數'],text_r))
    method.extend(re.findall(patterns['招標方式'],text_r))
    start_date.extend(re.findall(patterns['公告日期'],text_r))
    end_date.extend(re.findall(patterns['截止日'],text_r))
    budget.extend(re.findall(patterns['預算金額'],text_r))
    website.extend(re.findall(patterns['標案網址'],text_r))
website = ['https://web.pcc.gov.tw/tps'+i for i in website]

dict1 = {'機關名稱':company_name,'標案名稱':case_name,
         '標案公告次數': announce_times,'招標方式':method,
        '公告日期':start_date,'截止日':end_date,
        '預算金額':budget,'標案網址':website}
df = pd.DataFrame(dict1)
print('查詢結果共有'+str(len(df))+'筆資料')
end_date_list = df['截止日'].str.split('/')
for n in end_date_list:
    remain_days.append((datetime.datetime(int(n[0])+1911, \
    int(n[1]),int(n[2]))- datetime.datetime.today()).days+1)
df['剩餘天數'] = remain_days
df = df[df['剩餘天數']>0]
print('篩選標案剩餘天數，共'+str(len(df))+'筆資料')
np_case_name = df['標案名稱'].str
np_method = df['招標方式'].str


#篩選條件
condition = (np_case_name.contains('團體') | np_case_name.contains('鄉民') | \
np_case_name.contains('區民') | np_case_name.contains('鎮民') | \
np_case_name.contains('市民') | np_case_name.contains('義勇') | \
np_case_name.contains('義消') | np_case_name.contains('志工') | \
np_case_name.contains('守望相助')) & \
~np_case_name.contains('開口合約') & \
~np_case_name.contains('責任') & \
~np_method.contains('限制性') 

df = df[condition]
df['標案時程'] = (df['標案公告次數'] == '01') | (df['剩餘天數'] >=7)
df['標案時程'] = df['標案時程'].map({True:'尚有時間', False:'即將截止'})
      
print('篩選團險件標案，共'+str(len(df))+'筆資料')

df = df.sort_values('剩餘天數')
df.reset_index(drop = True,inplace = True)

df.to_csv('upload_case_data.csv',encoding='utf_8_sig',index=False)
