import upbit_coin_api as up
import pandas as pd
import requests
import json
from tabulate import tabulate
import time
import datetime

#time.sleep(900)
url = "https://api.upbit.com/v1/candles/days"
coin_response = requests.request("GET", "https://api.upbit.com/v1/market/all", params={"isDetails":"false"})
total_coin_name = {i["market"]:i["korean_name"]  for i in json.loads(coin_response.text)}
total_coin_name["KRW-KRW"] = "원화"
kor_coin_name = [i for i in total_coin_name if "KRW" in i]
#["KRW-DOGE","KRW-EOS","KRW-ADA","KRW-BCHA","KRW-QTUM","KRW-XRP","KRW-VET","KRW-DOT","KRW-XLM"],

million = '' #내 보유량
def my_bank(): #나의 보유량 업데이트
    global million
    million = ""
    million = pd.DataFrame(data=[[i[0],total_coin_name[i[0]], i[1], i[2]] for i in up.jango()], columns=["코인명", "한글명", "매수가","보유량"])
    million = million.set_index("코인명")

my_bank() #내 보유코인 업데이트
san = dict()
for i in million.index.tolist():
    san[i] = float(0.0) 

def c_detail(coin_name):#현재 시세    #c_detail("KRW-BTT") #예제 실행
    global san
    url = "https://api.upbit.com/v1/candles/days"
    querystring = {"market":coin_name,"count":"1"}    
    #querystring = {"market":coin_name,"to":"2021-04-23 09:00:01","count":"1"}    #날짜용
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
    return [yester, today, low, high, now_deep, deep, higher, low_per, higher_per]

def total_val(): #전체현황
    cate = ["어제","현재","최저가","최고가","현재퍼","최저퍼","최고퍼", "최저비", "최고비"]
    ncha = pd.DataFrame(index=cate).T
    for n, i in enumerate(kor_coin_name[:-1]):
        print(("*"*(len(kor_coin_name)-n-1))+(" "*(n+1)), end="\r", flush=True)
        ncha.loc[i] = c_detail(i)
        time.sleep(0.3)    
    ncha["한글명"] = [total_coin_name[i] for i in list(ncha.index)]
    ncha = ncha[["한글명","어제","현재","최저가","최고가","현재퍼","최저퍼","최고퍼", "최저비", "최고비"]]
    return ncha

def val_change(x): #구매금액 구하기    
    if x <= 10000: #만원 이하
        x = 15000
    elif x > 10001 and x <=25000: #만원 이상 25000원 이하
        x = 20000
    elif x > 25001 and x <=45000: #25000원 초과 45000원 이하
        x = 25000
    elif x > 45001 and x <=70000: #45000원 초과 700000원 이하
        x = 30000
    elif x > 70001 and x <=135000: #70000원 초과 135000원 이하
        x = 35000
    elif x > 135001 and x <=175000: #135000원 초과 175000원 이하
        x = 40000
    elif x > 175001 and x <=220000:  #175000원 초과 220000원 이하
        x = 45000    
    # elif x > 220001 and x <=270000:
    #     x = 50000
    # elif x > 270001 and x <=320000:
    #     x = 55000
    # elif x > 320001 and x <=370000:
    #     x = 60000
    # elif x > 370001 and x <=420000:
    #     x = 65000
    else:
        x = 50000
    return x

while True:        
    #파일값을읽어와서 적용하기 #보여지는 퍼센트 따로 저장하기
    with open("stats.json", "r", encoding='UTF-8-sig') as sta:
        stats = (lambda x : [x["상태"], x["최저비"], x["최저퍼"], x["표시최저비"], x["표시현재퍼"], x["적용코인"], x["매도퍼센트"]])(json.load(sta))    
    cate = ["어제","현재","최저가","최고가","현재퍼","최저퍼","최고퍼", "최저비", "최고비"]            
    low_co = pd.DataFrame(index=cate).T    

    for n, i in enumerate(stats[5]): #현재 금액 구하기       
        low_co.loc[i] = c_detail(i)#데이터프레임에 넣기                
        r_now = list(low_co.loc[i])[1] #현재가격 float
        r_nper = list(low_co.loc[i])[4] #현재 퍼센트
        r_lowp = list(low_co.loc[i])[7] #현재 최저비
        kname = total_coin_name[i] #코인 한글명
        m_in_co = million.index.tolist() #내가 가진 코인코드 리스트                            
        m_krw = float(million.loc["KRW-KRW"]["보유량"]) #내가 현재 가진 현금
        
        if r_lowp <= stats[1] and r_nper <= stats[2]: #실전 #json 파일에서 불러온 값 적용       
            if i in m_in_co: #내가 보유한 현황중 있다면. #1.현재 금액대비 퍼센트 계산한다. 2. 22%가 넘으면, 코드와 구매수량을 가져온다. 3. 시장가 매도를 한다                
                m_cnt = float(million.loc[i]["보유량"]) #내가 산 코인의 보유량                                
                m_inval = float(million.loc[i]["매수가"]) #내가 산 코인의 매수가
                buy_chip = val_change(round(m_inval * m_cnt)) #구매한 금액 대비 내가 살수있는 금액.
                if m_inval >= r_now: #해당 코인의 가격이 내가 구매한 값보다 작거나 같다면.
                    if m_krw >= buy_chip: #잔액이 구매할 금액보다 많다면. 
                        if float(san[i]) == 0.0: #내 구매코인안에는 있지만 오늘 처음 산거라면, 0.0에서 시작하니까 일단 사
                            san[i] = r_now #히스토리에 기록하고                        
                            print("[{}] up.maket_buy_order({}, {}) 1st ".format(kname, i, buy_chip))
                            if stats[0] == 1: 
                                up.maket_buy_order(i, str(buy_chip))
                                my_bank()
                            else:
                                print("{} 현재는 구매상태가 아니다.".format(kname))
                            with open("log.txt", "a") as f:
                                f.writelines("[{}] up.maket_buy_order({}, {}) 구매금액 {} -시간{} 1st".format(kname, i, buy_chip, str(r_now), datetime.datetime.now())  + "\n")
                        elif float(san[i]) != 0.0: #한번 더 구매한 코인인 경우 0.0에서 1번 구매한 코인
                            if float(san[i]) > r_now:   #오늘 구매 코인인데, 히스토리에 산 금액보다 작을경우에만 사                     
                                print("{} 이전 구매 금액은{}원 현재 구매 금액 {}원".format(kname, float(san[i]), r_now))
                                if stats[0] == 1: 
                                    up.maket_buy_order(i, str(buy_chip))
                                    my_bank()
                                    print("[{}] up.maket_buy_order({}, {}) 2nd".format(kname, i, buy_chip))                
                                    san[i] = r_now #히스토리에 기록해                            
                                    with open("log.txt", "a") as f:
                                        f.writelines("[{}] up.maket_buy_order({}, {}) 구매금액 {} -시간 {} 2nd".format(kname, i, buy_chip, str(r_now), datetime.datetime.now())  + "\n")                                                            
                                else:
                                    print("{} 현재는 구매상태가 아니다.".format(kname))
                            if float(san[i]) <= r_now:   #오늘 구매 코인인데, 히스토리에 산 금액보다 같거나 크다.
                                print("{} 오늘 구매했는데, 내가 산 금액보다 현재 시세가 높다. (예외1)".format(kname))
                                with open("log.txt", "a") as f:
                                    f.writelines("{} 오늘 구매했는데, 내가 산 금액보다 현재 시세가 높다. (예외1)".format(kname) + "\n")
                    else: #보유금이 없는 경우
                        print("내 보유금이 부족하니까 못사네 사지마 (예외2)")
                        with open("log.txt", "a") as f:
                            f.writelines("[{}]는 사기엔 내 보유금이 부족하니까 못사네 사지마 (예외2)".format(kname) + "\n")
                else: #내 보유한 코인 중 매수희망가가 높아서 안되는경우
                    print("[{}]는 이미 있고, 내 매수가가 낮아서 안산다. (예외3)".format(kname))
                    with open("log.txt", "a") as f:
                        f.writelines("[{}]는 이미 있고, 내 매수가가 낮아서 안산다. (예외3)".format(kname) + "\n")
            else: #내 구매목록에 없는거 살때 추가하기 
                print("구매목록이 없어 구매한다.")                       
                san[i] = r_now
                if stats[0] == 1:
                    time.sleep(0.2) 
                    up.maket_buy_order(i, "10000")
                    my_bank()
                    print("[{}] up.maket_buy_order({}, 10000) end".format(kname,i))
                    with open("log.txt", "a") as f:
                        f.writelines("[{}] up.maket_buy_order({}, 10000) 구매금액 {}원 -시간 {} end ".format(kname, i, str(r_now), datetime.datetime.now())  + "\n")        
                else:
                    print("{} 현재는 구매상태가 아니다.".format(kname))
        else: #대상 코인이 아니라 사지 못한다. 현재 현황을 보여준다.            
            if i in million.index.to_list(): #내가 가진 코인일경우
                mesuga = float(million.loc[i]["매수가"])  #내가 가진 코인의 매수한 가격       
                vourang = float(million.loc[i]["보유량"]) #내가 산 코인의 보유량                                
                my_percent = round((r_now - mesuga)/mesuga*100, 2) #현재 이득 퍼센트
                if stats[0] == 1: #상태 온오프 온상태                    
                    if my_percent >= stats[6]: #json파일 설정에 따라감  #매도 퍼센트                        
                        print("On[{},{}매{}] 최저비 {}, [{}]  현재 {}% 이득이다. 팔자! 매도! 매도!".format(stats[2], stats[1], stats[6], r_lowp, kname, my_percent))                        
                        print(up.maket_sell_order(i, vourang)) 
                        my_bank()
                        with open("log.txt", "a") as f:
                            f.writelines("[{}] up.maket_sell_order({}, {}) -시간 {} end ".format(kname, i, vourang, datetime.datetime.now())  + "\n")        

                    else: #그 이하일경우
                        print("On[퍼{},최저비{} 매도{}] 최저비 {}, [{}]  현재 {}% 이다. 존버! 존버!".format(stats[2], stats[1], stats[6], r_lowp, kname, my_percent))                        
                else:
                    print("Off[{},{}매도{}] 최저비 {}, [{}]".format(stats[2], stats[1], stats[6], r_lowp, kname))                
            else: #내가 가지고 있지 않은 코인일경우
                if stats[0] == 1: #상태 온오프 온상태
                    print("On[퍼{},최저비{} 매도{}] 최저비 {}, [{}]                               ".format(stats[2], stats[1], stats[6], r_lowp, kname))
                else:
                    print("Off[{},{},매{}] 최저비 {}, [{}]".format(stats[2], stats[1], stats[6], r_lowp, kname))                
        
        time.sleep(0.2) #0.2    
         
    low_co["한글명"] = [total_coin_name[i] for i in list(low_co.index)]
    low_co = low_co[["한글명","어제","현재","최저가","최고가","현재퍼","최저퍼","최고퍼", "최저비", "최고비"]]

    if len(low_co[(low_co['최저비'] <= stats[3]) & (low_co['현재퍼'] <= stats[4])].sort_values(["최저비"], ascending=True)) != 0: #현황이 있을때만 표시할것.!        
        print(tabulate(low_co[(low_co['최저비'] <= stats[3]) & (low_co['현재퍼'] <= stats[4])].sort_values(["최저비"], ascending=True)[["한글명","현재","현재퍼","최저퍼","최저비"]], ["한글명","현재","현재퍼","최저퍼","최저비"], tablefmt="grid"))        
    
    #time.sleep(300) #10분후


#손절하기 시장가 판매
#print((lambda x : up.maket_sell_order(x[0], x[1]))((lambda x : [million.loc[x].name, million.loc[x]["보유량"]])("KRW-ZIL")))

#모든 코인 한번에 시장가 판매
# for i in million.index.to_list()[1:]:    
#     print(up.maket_sell_order(i, million.loc[i]["보유량"]))    
#     time.sleep(0.2)

#코드랑 보유량
# for i in million.index.to_list():
#     (lambda x : [million.loc[x].name, million.loc[x]["보유량"]])(i)

#9시전에 전체 현황 한번 저장해두기
#cc = total_val()
# # cc.to_excel('0423_low.xlsx', encoding = 'UTF-8-SIG') 