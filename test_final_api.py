#!/usr/bin/env python3
import requests
import json
from datetime import datetime, timedelta

def test_all_apis():
    """나라장터 모든 API 종합 테스트"""
    
    # 실제 API 키
    service_key = "IShTX5OFowHN6eDSaOVglEh3a3DE5aqDpk2XopebFZM9joF7v/oDnjeGbg0RAC8fr2TJ2O5ip6BYwodpk1W7fA=="
    
    print("=" * 60)
    print("나라장터 API 종합 연결 테스트")
    print("=" * 60)
    
    # 1. 공공데이터개방표준서비스 - 입찰공고정보
    print("\n[1] 입찰공고정보 API 테스트")
    print("-" * 60)
    
    bid_url = "http://apis.data.go.kr/1230000/ao/PubDataOpnStdService/getDataSetOpnStdBidPblancInfo"
    bid_params = {
        'serviceKey': service_key,
        'type': 'json',
        'bidNtceBgnDt': '202501010000',  # 1월 1일부터
        'bidNtceEndDt': '202501312359',  # 1월 31일까지 (1개월 제한)
        'numOfRows': '10',
        'pageNo': '1'
    }
    
    try:
        response = requests.get(bid_url, params=bid_params, timeout=10)
        print(f"URL: {bid_url}")
        print(f"응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'response' in data:
                    header = data.get('response', {}).get('header', {})
                    body = data.get('response', {}).get('body', {})
                    
                    result_code = header.get('resultCode')
                    result_msg = header.get('resultMsg')
                    
                    print(f"결과: {result_code} - {result_msg}")
                    
                    if result_code == '00':
                        total_count = body.get('totalCount', 0)
                        items = body.get('items', [])
                        print(f"✅ 성공! 전체 {total_count}건 중 {len(items) if isinstance(items, list) else 1}건 조회")
                        
                        if items and isinstance(items, list) and len(items) > 0:
                            item = items[0]
                            print(f"  - 공고번호: {item.get('bidNtceNo', 'N/A')}")
                            print(f"  - 공고명: {item.get('bidNtceNm', 'N/A')[:50]}...")
                            print(f"  - 발주기관: {item.get('dminsttNm', 'N/A')}")
                    else:
                        print(f"⚠️ API 오류: {result_msg}")
                else:
                    print("❌ 예상과 다른 응답 형식")
                    print(f"응답: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
            except json.JSONDecodeError:
                print("❌ JSON 파싱 실패")
                print(f"응답: {response.text[:500]}")
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            print(f"응답: {response.text[:500]}")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    
    # 2. 공공데이터개방표준서비스 - 낙찰정보
    print("\n[2] 낙찰정보 API 테스트")
    print("-" * 60)
    
    scsbid_url = "http://apis.data.go.kr/1230000/ao/PubDataOpnStdService/getDataSetOpnStdScsbidInfo"
    scsbid_params = {
        'serviceKey': service_key,
        'type': 'json',
        'opengBgnDt': '202501010000',  # 1월 1일부터
        'opengEndDt': '202501072359',  # 1월 7일까지 (1주일 제한)
        'numOfRows': '10',
        'pageNo': '1'
    }
    
    try:
        response = requests.get(scsbid_url, params=scsbid_params, timeout=10)
        print(f"URL: {scsbid_url}")
        print(f"응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'response' in data:
                    header = data.get('response', {}).get('header', {})
                    body = data.get('response', {}).get('body', {})
                    
                    result_code = header.get('resultCode')
                    result_msg = header.get('resultMsg')
                    
                    print(f"결과: {result_code} - {result_msg}")
                    
                    if result_code == '00':
                        total_count = body.get('totalCount', 0)
                        items = body.get('items', [])
                        print(f"✅ 성공! 전체 {total_count}건 중 {len(items) if isinstance(items, list) else 1}건 조회")
                        
                        if items and isinstance(items, list) and len(items) > 0:
                            item = items[0]
                            print(f"  - 입찰공고번호: {item.get('bidNtceNo', 'N/A')}")
                            print(f"  - 낙찰업체: {item.get('scsbidCorpNm', 'N/A')}")
                            print(f"  - 낙찰금액: {item.get('scsbidAmt', 'N/A'):,}원" if item.get('scsbidAmt') else "  - 낙찰금액: N/A")
                    else:
                        print(f"⚠️ API 오류: {result_msg}")
                else:
                    print("❌ 예상과 다른 응답 형식")
            except json.JSONDecodeError:
                print("❌ JSON 파싱 실패")
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    
    # 3. 공공데이터개방표준서비스 - 계약정보
    print("\n[3] 계약정보 API 테스트")
    print("-" * 60)
    
    cntrct_url = "http://apis.data.go.kr/1230000/ao/PubDataOpnStdService/getDataSetOpnStdCntrctInfo"
    cntrct_params = {
        'serviceKey': service_key,
        'type': 'json',
        'cntrctCnclsBgnDate': '20250101',  # 1월 1일부터
        'cntrctCnclsEndDate': '20250131',  # 1월 31일까지
        'numOfRows': '10',
        'pageNo': '1'
    }
    
    try:
        response = requests.get(cntrct_url, params=cntrct_params, timeout=10)
        print(f"URL: {cntrct_url}")
        print(f"응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'response' in data:
                    header = data.get('response', {}).get('header', {})
                    result_code = header.get('resultCode')
                    result_msg = header.get('resultMsg')
                    
                    print(f"결과: {result_code} - {result_msg}")
                    
                    if result_code == '00':
                        body = data.get('response', {}).get('body', {})
                        total_count = body.get('totalCount', 0)
                        print(f"✅ 성공! 전체 {total_count}건 조회")
                    else:
                        print(f"⚠️ API 오류: {result_msg}")
                else:
                    print("❌ 예상과 다른 응답 형식")
            except json.JSONDecodeError:
                print("❌ JSON 파싱 실패")
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    
    print("\n" + "=" * 60)
    print("API 테스트 완료")
    print("=" * 60)
    
    print("\n📌 Flask 애플리케이션에서 사용하려면:")
    print("1. 서버 재시작: kill $(ps aux | grep 'python3 src/main.py' | grep -v grep | awk '{print $2}')")
    print("2. 서버 시작: cd /home/ls/nara1/나라장터\\ api/narajangter_app && python3 src/main.py &")
    print("3. 웹 접속: http://localhost:5000")

if __name__ == "__main__":
    test_all_apis()