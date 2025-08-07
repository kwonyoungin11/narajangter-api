#!/usr/bin/env python3
import requests
import json
from datetime import datetime, timedelta

def test_scsbid_api():
    """나라장터 낙찰정보 API 연결 테스트"""
    
    # API 엔드포인트 (낙찰정보서비스)
    api_url = "http://apis.data.go.kr/1230000/ScsbidInfoService04/getScsbidListSttusThng04"
    
    # 실제 API 키
    service_key = "IShTX5OFowHN6eDSaOVglEh3a3DE5aqDpk2XopebFZM9joF7v/oDnjeGbg0RAC8fr2TJ2O5ip6BYwodpk1W7fA=="
    
    # 테스트 파라미터
    params = {
        'serviceKey': service_key,
        'type': 'json',
        'inqryDiv': '1',  # 조회구분 (1: 개찰일시)
        'inqryBgnDt': '202501010000',
        'inqryEndDt': '202501312359',
        'numOfRows': '10',
        'pageNo': '1'
    }
    
    print("=" * 50)
    print("나라장터 낙찰정보 API 연결 테스트")
    print("=" * 50)
    print(f"API URL: {api_url}")
    print(f"조회 기간: {params['inqryBgnDt']} ~ {params['inqryEndDt']}")
    print("-" * 50)
    
    try:
        # API 호출
        print("API 호출 중...")
        response = requests.get(api_url, params=params, timeout=10)
        
        # 응답 상태 확인
        print(f"응답 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ API 연결 성공!")
            
            # 응답 형식 확인
            content_type = response.headers.get('Content-Type', '')
            print(f"응답 형식: {content_type}")
            
            # JSON 파싱 시도
            try:
                data = response.json()
                
                # 응답 구조 확인
                if 'response' in data:
                    header = data.get('response', {}).get('header', {})
                    body = data.get('response', {}).get('body', {})
                    
                    # 결과 코드 확인
                    result_code = header.get('resultCode', 'Unknown')
                    result_msg = header.get('resultMsg', 'Unknown')
                    
                    print(f"결과 코드: {result_code}")
                    print(f"결과 메시지: {result_msg}")
                    
                    if result_code == '00':
                        # 데이터 확인
                        items = body.get('items', [])
                        total_count = body.get('totalCount', 0)
                        
                        print(f"전체 건수: {total_count}")
                        
                        if items:
                            print(f"조회된 낙찰 수: {len(items) if isinstance(items, list) else 1}")
                            
                            # 첫 번째 낙찰 정보 출력
                            first_item = items[0] if isinstance(items, list) else items
                            print("\n첫 번째 낙찰 정보:")
                            print(f"  - 입찰공고번호: {first_item.get('bidNtceNo', 'N/A')}")
                            print(f"  - 낙찰업체명: {first_item.get('scsbidCorpNm', 'N/A')}")
                            print(f"  - 낙찰금액: {first_item.get('scsbidAmt', 'N/A')}")
                        else:
                            print("조회된 낙찰정보가 없습니다.")
                    else:
                        print(f"⚠ API 응답 오류: {result_msg}")
                else:
                    print("예상치 못한 응답 형식입니다.")
                    print(f"응답 내용: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
                    
            except json.JSONDecodeError as e:
                print(f"✗ JSON 파싱 실패: {e}")
                print(f"응답 내용 (처음 500자): {response.text[:500]}")
                
        else:
            print(f"✗ API 호출 실패: HTTP {response.status_code}")
            print(f"응답 내용: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print("✗ API 호출 시간 초과")
    except requests.exceptions.ConnectionError as e:
        print(f"✗ 연결 오류: {e}")
    except Exception as e:
        print(f"✗ 예기치 않은 오류: {e}")
        
    print("=" * 50)

if __name__ == "__main__":
    test_scsbid_api()