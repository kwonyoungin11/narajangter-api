#!/usr/bin/env python3
"""
나라장터 API 테스트 - URL 인코딩 문제 해결 버전
"""
import requests
import urllib.parse
from datetime import datetime, timedelta

def test_all_apis_fixed():
    """URL 인코딩 문제를 해결한 API 테스트"""
    
    # 이미 URL 인코딩된 서비스 키 (그대로 사용)
    SERVICE_KEY_ENCODED = "IShTX5OFowHN6eDSaOVglEh3a3DE5aqDpk2XopebFZM9joF7v%2FoDnjeGbg0RAC8fr2TJ2O5ip6BYwodpk1W7fA%3D%3D"
    SERVICE_KEY_DECODED = "IShTX5OFowHN6eDSaOVglEh3a3DE5aqDpk2XopebFZM9joF7v/oDnjeGbg0RAC8fr2TJ2O5ip6BYwodpk1W7fA=="
    
    print("=" * 70)
    print("나라장터 API 테스트 - URL 인코딩 문제 해결")
    print("=" * 70)
    
    # 테스트할 API 엔드포인트들
    apis = [
        {
            "name": "입찰공고정보 (공공데이터개방표준)",
            "url": "https://apis.data.go.kr/1230000/PubDataOpnStdService04/getDataSetOpnStdBidPblancInfo04",
            "params": {
                "type": "json",
                "numOfRows": "10",
                "pageNo": "1",
                "bidNtceBgnDt": "202501010000",
                "bidNtceEndDt": "202501012359"
            }
        },
        {
            "name": "입찰공고정보 (BidPublicInfoService04)",
            "url": "https://apis.data.go.kr/1230000/BidPublicInfoService04/getBidPblancListInfoServcPPSSrch04",
            "params": {
                "type": "json",
                "numOfRows": "10",
                "pageNo": "1",
                "inqryDiv": "1",
                "inqryBgnDt": "202501010000",
                "inqryEndDt": "202501012359"
            }
        },
        {
            "name": "낙찰정보 (ScsbidInfoService04)",
            "url": "https://apis.data.go.kr/1230000/ScsbidInfoService04/getScsbidListSttusThng04",
            "params": {
                "type": "json",
                "numOfRows": "10",
                "pageNo": "1",
                "inqryDiv": "1",
                "inqryBgnDt": "202501010000",
                "inqryEndDt": "202501072359"
            }
        }
    ]
    
    for api_info in apis:
        print(f"\n[테스트] {api_info['name']}")
        print("-" * 70)
        print(f"URL: {api_info['url']}")
        
        # 방법 1: requests 라이브러리가 자동으로 인코딩하도록
        print("\n방법 1: Decoded 키 사용 (requests가 자동 인코딩)")
        params1 = api_info['params'].copy()
        params1['ServiceKey'] = SERVICE_KEY_DECODED
        
        try:
            resp1 = requests.get(api_info['url'], params=params1, timeout=10)
            print(f"  상태 코드: {resp1.status_code}")
            
            if resp1.status_code == 200:
                try:
                    data = resp1.json()
                    if 'response' in data:
                        result_code = data['response']['header'].get('resultCode')
                        result_msg = data['response']['header'].get('resultMsg')
                        print(f"  결과: {result_code} - {result_msg}")
                        
                        if result_code == '00':
                            total = data['response']['body'].get('totalCount', 0)
                            print(f"  ✅ 성공! 전체 {total}건")
                    else:
                        print(f"  ❌ 응답 형식 오류")
                except:
                    print(f"  ❌ JSON 파싱 실패")
                    if resp1.text.startswith('<?xml'):
                        print(f"  XML 응답: {resp1.text[:200]}")
            else:
                print(f"  ❌ HTTP 오류: {resp1.status_code}")
                print(f"  응답: {resp1.text[:200]}")
        except Exception as e:
            print(f"  ❌ 오류: {e}")
        
        # 방법 2: 이미 인코딩된 키를 URL에 직접 포함
        print("\n방법 2: Encoded 키를 URL에 직접 포함")
        params2 = api_info['params'].copy()
        
        # 파라미터를 수동으로 구성
        query_parts = []
        for key, value in params2.items():
            query_parts.append(f"{key}={value}")
        query_parts.append(f"ServiceKey={SERVICE_KEY_ENCODED}")
        
        full_url = f"{api_info['url']}?{'&'.join(query_parts)}"
        
        try:
            resp2 = requests.get(full_url, timeout=10)
            print(f"  상태 코드: {resp2.status_code}")
            
            if resp2.status_code == 200:
                try:
                    data = resp2.json()
                    if 'response' in data:
                        result_code = data['response']['header'].get('resultCode')
                        result_msg = data['response']['header'].get('resultMsg')
                        print(f"  결과: {result_code} - {result_msg}")
                        
                        if result_code == '00':
                            total = data['response']['body'].get('totalCount', 0)
                            print(f"  ✅ 성공! 전체 {total}건")
                    else:
                        print(f"  ❌ 응답 형식 오류")
                except:
                    print(f"  ❌ JSON 파싱 실패")
            else:
                print(f"  ❌ HTTP 오류: {resp2.status_code}")
        except Exception as e:
            print(f"  ❌ 오류: {e}")
    
    print("\n" + "=" * 70)
    print("테스트 완료")
    print("=" * 70)
    
    print("\n📌 권장사항:")
    print("1. HTTPS 사용 (HTTP 대신)")
    print("2. ServiceKey 파라미터명 정확히 사용 (대소문자 구분)")
    print("3. 필수 파라미터 누락 확인 (type, numOfRows, pageNo)")
    print("4. API 버전 확인 (Service04 등 최신 버전)")
    print("5. 날짜 범위 제한 확인 (입찰공고 1개월, 낙찰정보 1주일)")

if __name__ == "__main__":
    test_all_apis_fixed()