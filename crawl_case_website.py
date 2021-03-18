# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 15:04:52 2021

@author: 00549879
"""

import csv , requests ,random , re , datetime
from fake_useragent import UserAgent
import pandas as pd
import requests.packages.urllib3
import streamlit as st
import base64
from io import BytesIO
st.title('招標網團險案件查詢')
st.markdown('即時搜尋政府招標網，篩選團險案件')
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

關鍵字 = st.text_input("搜尋關鍵字(預設為：險)",value='險')
st.markdown('篩選關鍵字具其一則顯示，可自行修改')
st.markdown('如欲搜尋防汛，可將其中一項條件改為防汛，不需之條件輸入X)')
關鍵字2_1 = st.text_input("篩選關鍵字包含(1)",value='團體')
關鍵字2_2 = st.text_input("篩選關鍵字包含(2)",value='鄉民')
關鍵字2_3 = st.text_input("篩選關鍵字包含(3)",value='區民')
關鍵字2_4 = st.text_input("篩選關鍵字包含(4)",value='鎮民')
關鍵字2_5 = st.text_input("篩選關鍵字包含(5)",value='市民')
關鍵字2_6 = st.text_input("篩選關鍵字包含(6)",value='義勇')
關鍵字2_7 = st.text_input("篩選關鍵字包含(7)",value='義消')
關鍵字2_8 = st.text_input("篩選關鍵字包含(8)",value='志工')
關鍵字2_9 = st.text_input("篩選關鍵字包含(9)",value='守望相助')
st.markdown('篩選關鍵字不含條件，具其一則不顯示')
關鍵字2_10 = st.text_input("篩選關鍵字不包含(1)",value='開口合約')
關鍵字2_11 = st.text_input("篩選關鍵字不包含(2)",value='責任')




#是否等標期間 = st.text_input("是否等標期間(N / Y)(半形)",value='N')
是否等標期間 = 'N'
today = datetime.datetime.today()
days = datetime.timedelta(days = 40)
s = st.date_input('公告日起日(預設為40天前)',datetime.date((today-days).year,
                                       (today-days).month, (today-days).day))
查詢起日 = str(int(str(s)[:4])-1911)+'/'+str(s)[5:7]+'/'+str(s)[8:]
d = st.date_input('公告日迄日(預設為今日)',datetime.date(today.year, today.month, today.day))
查詢迄日 = str(int(str(d)[:4])-1911)+'/'+str(d)[5:7]+'/'+str(d)[8:]


#st.write(d)
#st.write('test is:', str(int(str(d)[:4])-1911)+'/'+str(d)[5:7]+'/'+str(d)[8:])
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    val = to_excel(df)
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="case.xlsx"> >>下載檔案<< </a>' 

    

def crawling():
    import requests , re , datetime ,time ,os
    from fake_useragent import UserAgent
    import pandas as pd
    import requests.packages.urllib3
    from pandas import ExcelWriter
    import openpyxl , xlrd
    from openpyxl.styles import Font, colors, Border, Side
    requests.packages.urllib3.disable_warnings()
    ua = UserAgent()
    headers = {'User-Agent': ua.random}

    company_name = []
    case_name = []
    case_num = []
    announce_times = []
    method = []
    start_date = []
    end_date = []
    budget = []
    remain_days = []
    website = []
    #csv_reader = open('查詢條件設定.csv','r')
    search_keys = {}
    search_keys[1] = 關鍵字
    search_keys[2] = 是否等標期間
    search_keys[3] = 查詢起日
    search_keys[4] = 查詢迄日

    #for index, line in enumerate(csv_reader.read().splitlines(),start = 1):
    #    search_keys[index] = line.split(',')[1]

    today = datetime.datetime.today()
    days = datetime.timedelta(days = 40)
    if search_keys[4] == 'N':
        search_keys[4] = str(today.year-1911)+'/'+str(today.month).zfill(2)+'/'+str(today.day).zfill(2)
    if search_keys[3] == 'N':
        search_keys[3] = str((today-days).year-1911)+'/'+str((today-days).month).zfill(2)+'/'+str((today-days).day).zfill(2)
    print('查詢時間範圍: ',search_keys[3],'-->',search_keys[4])

    url = 'https://web.pcc.gov.tw/tps/pss/tender.do?searchMode=common&searchType=basic'
    patterns = { \
        '機關名稱' : '機關名稱 -->.*?<td align="left">(.*?)&' ,
        '標案名稱' : '標案名稱 -->.*?title="(.*?)"',
        '標案案號' : '標案名稱 -->.*?<td align="left">.*?([^\t\r].*?)\r',
        '標案公告次數' : '<!-- 傳輸次數.*?title="(.*?)"',
        '招標方式' : '<!-- 招標方式.*?"left">(.*?)</td>',
        '公告日期' : '<!-- 公告日期.*?"left">(.*?)</td>',
        '截止日' : '<!-- 截止投標.*?"left">(.*?)</td>',
        '預算金額' : '<!-- 預算金額.*?(\d.*?)\D',
        '標案網址' : '標案名稱 -->.*?<a href="..(.*?)" title="'
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
    #text_r = r.text.replace('\n','')
    data_num = eval(re.findall('共有.*>(.*)</span>', r.text)[0])
    page_turn = data_num//100

    for i in range(page_turn+1):
        page = str(i+1)
        print('招標網爬取第',page,'頁')
        r = session.get('https://web.pcc.gov.tw/tps/pss/tender.do?searchMode=common&searchType=basic&method=search&isSpdt='+search_keys[2]+'&pageIndex='+page,headers = headers,verify=False)
        text_r = r.text.replace('\n','')
        company_name.extend(re.findall(patterns['機關名稱'], text_r))
        case_name.extend(re.findall(patterns['標案名稱'],text_r))
        case_num.extend(re.findall(patterns['標案案號'],text_r))
        announce_times.extend(re.findall(patterns['標案公告次數'],text_r))
        method.extend(re.findall(patterns['招標方式'],text_r))
        start_date.extend(re.findall(patterns['公告日期'],text_r))
        end_date.extend(re.findall(patterns['截止日'],text_r))
        budget.extend(re.findall(patterns['預算金額'],text_r))
        website.extend(re.findall(patterns['標案網址'],text_r))
    website = ['https://web.pcc.gov.tw/tps'+i for i in website]

    dict1 = {'機關名稱':company_name,'標案名稱':case_name,
             '標案案號':case_num,'標案公告次數': announce_times,
             '招標方式':method,'公告日期':start_date,'截止日':end_date,
            '預算金額':budget,'標案網址':website}
    df = pd.DataFrame(dict1)
    print('查詢結果共有'+str(len(df))+'筆資料')

    path = os.getcwd()
    out_path = '/'.join(path.split('/')[:-1])
    #df.to_csv(out_path+'\\all_case_data.csv',encoding='utf_8_sig',index=False)

    #print('匯出all_case_data.csv')
    end_date_list = df['截止日'].str.split('/')
    for n in end_date_list:
        remain_days.append(max((datetime.datetime(int(n[0])+1911, \
        int(n[1]),int(n[2]))- datetime.datetime.today()).days+1,0))
    df['剩餘天數'] = remain_days
    np_case_name = df['標案名稱'].str
    np_method = df['招標方式'].str


    #篩選條件
    condition = (np_case_name.contains(關鍵字2_1) | np_case_name.contains(關鍵字2_2) | \
    np_case_name.contains(關鍵字2_3) | np_case_name.contains(關鍵字2_4) | \
    np_case_name.contains(關鍵字2_5) | np_case_name.contains(關鍵字2_6) | \
    np_case_name.contains(關鍵字2_7) | np_case_name.contains(關鍵字2_8) | \
    np_case_name.contains(關鍵字2_9)) & \
    ~np_case_name.contains(關鍵字2_10) & \
    ~np_case_name.contains(關鍵字2_11) #& \
    #~np_method.contains('限制性') 

    df = df[condition]

    print('篩選團險件標案，共'+str(len(df))+'筆資料')

    #df = df.sort_values('剩餘天數')
    df = df.sort_values('公告日期',ascending=False)
    df.reset_index(drop = True,inplace = True)
    return df
    #path = os.getcwd()
    #out_path = out_path = '/'.join(path.split('/')[:-1])
    #df.to_csv('upload_case_data.csv',encoding='utf_8_sig',index=False)
    
start = st.button("開始執行")
if start:
    df = crawling()

try:
    st.markdown(get_table_download_link(df), unsafe_allow_html=True)
    st.table(df)
    st.markdown(關鍵字2_1,關鍵字2_2)
except:
    st.error('尚未執行')
