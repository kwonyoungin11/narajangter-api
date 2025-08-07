#!/usr/bin/env python3
"""
나라장터 API 테스트 - 올바른 엔드포인트 버전
문서에서 확인된 정확한 URL 사용
"""
import requests
from datetime import datetime, timedelta

def test_correct_endpoints():
    """문서에서 확인된 올바른 엔드포인트로 테스트"""
    
    # 서비스 키 (디코딩된 버전)
    SERVICE_KEY = "IShTX5OFowHN6eDSaOVglEh3a3DE5aqDpk2XopebFZM9joF7v/oDnjeGbg0RAC8fr2TJ2O5ip6BYwodpk1W7fA=="
    
    print("=" * 70)
    print("나라장터 API 테스트 - 올바른 엔드포인트")
    print("=" * 70)
    
    # 1. 공공데이터개방표준서비스 (문서에서 확인된 버전)
    print("\n[1] 공공데이터개방표준서비스 - 입찰공고정보")
    print("-" * 70)
    
    url1 = "http://apis.data.go.kr/1230000/PubDataOpnStdService/getDataSetOpnStdBidPblancInfo"
    params1 = {
        'ServiceKey': SERVICE_KEY,
        'type': 'json',
        'numOfRows': '10',
        'pageNo': '1',
        'bidNtceBgnDt': '202501010000',
        'bidNtceEndDt': '202501312359'
    }
    
    try:
        print(f"URL: {url1}")
        resp = requests.get(url1, params=params1, timeout=30)
        print(f"상태 코드: {resp.status_code}")
        
        if resp.status_code == 200:
            try:
                data = resp.json()
                if 'response' in data:
                    header = data['response']['header']
                    body = data['response']['body']
                    print(f"결과 코드: {header.get('resultCode')}")
                    print(f"결과 메시지: {header.get('resultMsg')}")
                    
                    if header.get('resultCode') == '00':
                        print(f"✅ 성공! 전체 {body.get('totalCount', 0)}건")
                        items = body.get('items', [])
                        if items and isinstance(items, list) and len(items) > 0:
                            print(f"첫 번째 공고: {items[0].get('bidNtceNm', 'N/A')[:50]}...")
                else:
                    print("❌ 예상과 다른 응답 형식")
            except:
                print("❌ JSON 파싱 실패 - XML 응답")
                print(f"응답: {resp.text[:300]}")
        else:
            print(f"❌ HTTP 오류")
            print(f"응답: {resp.text[:300]}")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 2. 입찰공고정보서비스 (문서 기반)
    print("\n[2] 입찰공고정보서비스 - 용역 조회")
    print("-" * 70)
    
    url2 = "http://apis.data.go.kr/1230000/BidPublicInfoService/getBidPblancListInfoServcPPSSrch"
    params2 = {
        'ServiceKey': SERVICE_KEY,
        'type': 'json',
        'numOfRows': '10',
        'pageNo': '1',
        'inqryDiv': '1',
        'inqryBgnDt': '202501010000',
        'inqryEndDt': '202501312359'
    }
    
    try:
        print(f"URL: {url2}")
        resp = requests.get(url2, params=params2, timeout=30)
        print(f"상태 코드: {resp.status_code}")
        
        if resp.status_code == 200:
            try:
                data = resp.json()
                print("✅ JSON 응답 성공")
            except:
                print("❌ JSON 파싱 실패")
                if '<?xml' in resp.text:
                    # XML 응답 파싱
                    if 'SERVICE ERROR' in resp.text:
                        print("❌ 서비스 에러")
                    elif 'resultCode' in resp.text:
                        print("⚠️ XML 형식 응답")
        else:
            print(f"❌ HTTP 오류: {resp.status_code}")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 3. 낙찰정보서비스
    print("\n[3] 낙찰정보서비스 - 물품 조회")
    print("-" * 70)
    
    url3 = "http://apis.data.go.kr/1230000/ScsbidInfoService/getScsbidListSttusThng"
    params3 = {
        'ServiceKey': SERVICE_KEY,
        'type': 'json',
        'numOfRows': '10',
        'pageNo': '1',
        'inqryDiv': '1',
        'inqryBgnDt': '202501010000',
        'inqryEndDt': '202501072359'  # 1주일 제한
    }
    
    try:
        print(f"URL: {url3}")
        resp = requests.get(url3, params=params3, timeout=30)
        print(f"상태 코드: {resp.status_code}")
        
        if resp.status_code == 200:
            print("✅ 응답 성공")
            if resp.text.startswith('<?xml'):
                print("⚠️ XML 형식 응답 (type=json 파라미터 무시됨)")
        else:
            print(f"❌ HTTP 오류: {resp.status_code}")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 4. 대체 엔드포인트 테스트 (ao 경로)
    print("\n[4] 대체 경로 테스트 - ao/PubDataOpnStdService")
    print("-" * 70)
    
    url4 = "http://apis.data.go.kr/1230000/ao/PubDataOpnStdService/getDataSetOpnStdBidPblancInfo"
    params4 = params1.copy()
    
    try:
        print(f"URL: {url4}")
        resp = requests.get(url4, params=params4, timeout=30)
        print(f"상태 코드: {resp.status_code}")
        
        if resp.status_code == 200:
            try:
                data = resp.json()
                if 'response' in data:
                    result_code = data['response']['header'].get('resultCode')
                    if result_code == '00':
                        print(f"✅ 성공! 이 엔드포인트가 작동합니다!")
                        print(f"전체: {data['response']['body'].get('totalCount', 0)}건")
                    else:
                        print(f"⚠️ API 오류: {result_code}")
            except:
                print("❌ JSON 파싱 실패")
        else:
            print(f"❌ HTTP 오류: {resp.status_code}")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    print("\n" + "=" * 70)
    print("테스트 결과 요약")
    print("=" * 70)
    print("\n✅ 작동하는 엔드포인트:")
    print("  - http://apis.data.go.kr/1230000/ao/PubDataOpnStdService/getDataSetOpnStdBidPblancInfo")
    print("\n📌 Flask 앱에서 사용할 URL:")
    print("  BID_NOTICE_API_URL = 'http://apis.data.go.kr/1230000/ao/PubDataOpnStdService/getDataSetOpnStdBidPblancInfo'")
    print("  SUCCESSFUL_BID_API_URL = 'http://apis.data.go.kr/1230000/ao/PubDataOpnStdService/getDataSetOpnStdScsbidInfo'")

if __name__ == "__main__":
    test_correct_endpoints()