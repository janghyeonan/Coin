# 업비트 코인거래 api를 이용한 봇(python 3.8)


## 1.패키지 설치 
pip install -r requirements.txt

## 1-1. PyJWT 패키지 설치시 재설치 필요
pip uninstall PyJWT
pip install PyJWT==1.7.1

## 2.업비트에 가서 엑서스키랑 시크릿키 수령
api 신청 후 엑서스키, 시크릿키 수령,
api사용할 아이피도 등록, 다른 아이피에서 사용불가

## 3.upbit_coin_api 파일에 엑서스키, 시크릿키 추가
upbit_coin_api에 본인의 키를 넣는다.

## 4.소스파일 파악하기
허접하지만 소스파일을 파악해서 사용한다.

## 5.설명
real_low.py : 최저가에 구매해서 수익이 나면 파는 것 구현
stats.json : 설정 세팅하는 파일
coin_log.py : 특정 코인 및 모든 코인의 동향 파악 가능한 내용 구현
upbit_coin_api.py : 업비트 api 사용하는 부분 구현

# 개인 용도로 구현해 놓은 것으로 허접합니다. 수정부분 혹은 지적사항 있으시면, 주저하지 마시고 ajh910@gmail.com으로 연락주세요.
