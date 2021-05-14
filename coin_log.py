import pandas as pd
import requests
import json
from tabulate import tabulate
import time
from datetime import datetime, timedelta

url = "https://api.upbit.com/v1/candles/days"
coin_response = requests.request("GET", "https://api.upbit.com/v1/market/all", params={"isDetails":"false"})
total_coin_name = {i["market"]:i["korean_name"]  for i in json.loads(coin_response.text)}
total_coin_name["KRW-KRW"] = "원화"
kor_coin_name = [i for i in total_coin_name if "KRW" in i]
cate = ["코인명","어제","현재","최저가","최고가","현재퍼","최저퍼","최고퍼", "최저비", "최고비"]
ncha = pd.DataFrame(index=cate).T
df = pd.DataFrame(columns=["market", "candle_date_time_utc", "candle_date_time_kst", "opening_price", "high_price", "low_price", "trade_price", "timestamp", "candle_acc_trade_price", "candle_acc_trade_volume", "unit"])

def c_detail(stats, coin_name, ddate):#현재 시세    #c_detail("KRW-BTT") #예제 실행
    global url
    if stats == 0:
        querystring = {"market":coin_name,"count":"1"}    #오늘
    elif stats == 1:
        querystring = {"market":coin_name,"to":ddate,"count":"1"}    #날짜용
    result = json.loads(requests.request("GET", url, params=querystring).text)    
    yester = result[0]["prev_closing_price"] #어제 금액    
    today = result[0]["trade_price"] #현재가    
    low = result[0]["low_price"] #최저가     
    deep = round((result[0]["low_price"] - result[0]["prev_closing_price"])/result[0]["prev_closing_price"]*100, 2) #당일최저가의 떨어진비율    
    higher = round((result[0]["high_price"] - result[0]["prev_closing_price"])/result[0]["prev_closing_price"]*100, 2) #당일최고가의 떨어진비율        
    now_deep = round(result[0]["change_rate"]*100, 2) #어제가 대비 현재가의 비율    
    low_per = round(now_deep-deep,2) #현재가가 최저가 대비 얼마인지
    higher_per = round(higher-now_deep,2) #현재가가 최고가 대비 얼마인지
    high = result[0]["high_price"] #최고가   
    return [total_coin_name[coin_name], yester, today, low, high, now_deep, deep, higher, low_per, higher_per]

def start(cnt,llist):
    global ncha
    for j in llist:
        print(j)
        for i in range(cnt, 0, -1):
            ddate = str(datetime.now() - timedelta(days=i))[0:10] + " 09:00:01"
            ncha.loc[ddate[0:10]+" "+j] = c_detail(1, j, ddate)
            time.sleep(0.2)

def total_val(): #전체현황
    global kor_coin_name
    cate = ["코인명", "어제","현재","최저가","최고가","현재퍼","최저퍼","최고퍼", "최저비", "최고비"]
    today = pd.DataFrame(index=cate).T
    for n, i in enumerate(kor_coin_name[:-1]):
        print(("*"*(len(kor_coin_name)-n-1))+(" "*(n+1)), end="\r", flush=True)
        today.loc[i] = c_detail(0, i, "2021-01-01")
        time.sleep(0.3)    
    today = today[["코인명","어제","현재","최저가","최고가","현재퍼","최저퍼","최고퍼", "최저비", "최고비"]]
    today.to_excel(str(datetime.now()).replace(" ","_").replace(":","-").split(".")[0] +'.xlsx', encoding = 'UTF-8-SIG')
    return today

# cc = total_val()

# cc[["최저퍼","최고퍼"]].sort_values(by=["최저퍼"], axis=0) #오름
# cc[["최저퍼","최고퍼"]].sort_values(by=["최저퍼"], axis=0, ascending=False) #내림

# cc[["최저퍼","최고퍼"]].sort_values(by=["최고퍼"], axis=0) #오름
# cc[["최저퍼","최고퍼"]].sort_values(by=["최고퍼"], axis=0, ascending=False) #내림

def min_list(coin_name, yy, mm, dd):
    global df
    #시간대별로 알아보기
    for i in range(60*24):
        tt = str(datetime(yy, mm, dd, 9, 00, 1) + timedelta(minutes=i))
        querystring = {"market":coin_name,"to":tt,"count":"1"}
        response = requests.request("GET", "https://api.upbit.com/v1/candles/minutes/1", params=querystring)
        result = json.loads(response.text)[0]
        df.loc[tt] = [values for keys, values in result.items()]
        print(i)
        time.sleep(0.1)
            #컬럼삭제
    df.drop(["candle_date_time_utc", "candle_date_time_kst", "opening_price", "high_price","trade_price", "timestamp", "candle_acc_trade_price", "candle_acc_trade_volume", "unit"], axis=1, inplace=True)
    #컬럼추가
    result2 = json.loads(requests.request("GET", "https://api.upbit.com/v1/candles/days", params={"market":coin_name,"to":str(datetime(yy, mm, dd, 9, 00, 1)),"count":"1"}).text)    
    df["yesterday"] = result2[0]["prev_closing_price"]
    df["per"] = (lambda x,y: round((x-y)/y*100,2))(df["low_price"], df["yesterday"])
    df = df[['per', 'market', 'low_price', 'yesterday']]
    #df.to_excel('0512_min.xlsx', encoding = 'UTF-8-SIG') 

if __name__ == '__main__': # 날짜 몇일부터 언제까지 조회할지 결정, 코인코드명 리스트로 넣어주면 나옴.
    #start(9,["KRW-ADA","KRW-DOT","KRW-STEEM"])
    #start(30,["KRW-ADA"])
    #print(tabulate(ncha, cate, tablefmt="grid"))
    min_list("KRW-ADA", 2021, 5, 12)
    print(df)