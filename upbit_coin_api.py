import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode
import requests
import json
import math
import time

access_key = "abc" #본인 엑서스키
secret_key = "abc" #본인 시크릿키
server_url = "https://api.upbit.com"

def jango(): #잔액 조회
    '''
    업비트 잔액을 조회해서 어떤 종목 평균매입가, 수량을 리턴해줌.
    '''
    global access_key,secret_key, server_url    
    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
    }
    jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.get(server_url + "/v1/accounts", headers=headers)    
    return [["KRW-"+i["currency"], i["avg_buy_price"], i["balance"]] for i in res.json()]
    #return [["KRW-"+i["currency"],i["avg_buy_price"], math.trunc(float(i["balance"]))] for i in res.json()]

def maket_buy_order(market, price): #시장가 매수
    '''    
    시장가 매수 함수
    ex) maket_buy_order("KRW-XLM","1000")
        : 마켓, 총 매수금액 
    # query = {
    #     'market': 'KRW-XLM',  ->코인명
    #     'side': 'bid',  ->매수 
    #     'price': '100000', ->총 매수금액 
    #     'ord_type': 'price' ->시장가
    # }
    '''
    global access_key,secret_key, server_url
    query = {
        'market': market,
        'side': "bid",
        'price': price,
        'ord_type': "price"}

    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()
    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.post(server_url + "/v1/orders", params=query, headers=headers)
    return res.json()

#206.18556701
#market = "KRW-SSX"
#volume = "206.18556701"
def maket_sell_order(market, volume): #시장가 매도
    '''    
    시장가 매도 함수 (가지고 있는 코인가 수량을 파악 후 실행할것.)
    ex) maket_sell_order("KRW-XLM","1000")
        : 마켓, 총 매수금액 
    # query = {
    #     'market': 'KRW-XLM',  ->코인명
    #     'side': 'ask',  ->매도
    #     'volume': '1000', 가지고 있던 수량
    #     'ord_type': 'price' ->시장가
    # }
    '''
    global access_key,secret_key, server_url
    query = {
        'market': market,
        'side': "ask",
        'volume': volume,
        'ord_type': "market"}
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()
    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.post(server_url + "/v1/orders", params=query, headers=headers)
    return res.json()

def order(market, side, volume, price): #매도  매수하는 함수 
    '''    
    시장가 매수시 order("KRW-XLM", "bid", "100", "200")
    : 마켓, 매수/매도 변수, 금액 
    지정가 매수시 order(market, side, volume, price)
    # query = {
    #     'market': 'KRW-SC',
    #     'side': 'bid'매수, 'ask'매도
    #     'volume': '1000', 수량
    #     'price': '7.49', 가격
    #     'ord_type': 'limit', price(시장가)
    # }
    '''
    global access_key,secret_key, server_url
    
    query = {
        'market': market,
        'side': side,
        'volume': volume,
        'price': price,
        'ord_type': "limit",
    }
    
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()
    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.post(server_url + "/v1/orders", params=query, headers=headers)
    return res.json()

#mg.mg_insert(res.json())
#mg.mycol.delete_one({"uuid":idid})

def order_cancel(idid):
    '''
    idid는 uuid를 넣으시오
    '''
    global access_key,secret_key, server_url
    query = {
        'uuid': idid,
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.delete(server_url + "/v1/order", params=query, headers=headers)
    print("취소되었습니다.")
    return res.json()

def order_check_list(): #미체결 현황을 리턴해주는 함수
    '''
    미체결현황 모두를 리스트로 리턴해주는 함수
    uuid를 리스트로 넣어준다.
    '''
    global access_key,secret_key, server_url
    query = {
        'state': 'wait',
    }
    query_string = urlencode(query)
    uuids = u_list()
    uuids_query_string = '&'.join(["uuids[]={}".format(uuid) for uuid in uuids])

    query['uuids[]'] = uuids
    query_string = "{0}&{1}".format(query_string, uuids_query_string).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.get(server_url + "/v1/orders", params=query, headers=headers)
    return [(i["market"], i["side"], i["state"]) for i in res.json()]

def json_my_wish(): #내 오더 리스트를 저장한 함수 불러오기
    '''
    json파일 불러와서 데이터 넘겨주기
    '''
    with open('order_list.json', 'r') as f:
        json_data = json.load(f)
    return json_data

def point_change(x): ##소수점 둘째자리는 마지막 자리를 0으로 만듬
    '''
    소수 둘째자리를 반올림해줘서 0으로 만들어 줌
    '''
    x = round(float(x)+float(x)*0.035,2)
    if len(str(x)) == 5:
        x = str(round(float(x), 1))+"0"
    return x