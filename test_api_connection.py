#!/usr/bin/env python3
import requests
import json
from datetime import datetime, timedelta

def test_narajangter_api():
    """나라장터 API 연결 테스트"""
    
    # API 엔드포인트 (입찰공고정보서비스 - 용역)
    api_url = "http://apis.data.go.kr/1230000/BidPublicInfoService04/getBidPblancListInfoServcPPSSrch04"
    
    # 실제 API 키
    service_key = "IShTX5OFowHN6eDSaOVglEh3a3DE5aqDpk2XopebFZM9joF7v/oDnjeGbg0RAC8fr2TJ2O5ip6BYwodpk1W7fA=="
    
    # 테스트 파라미터
    params = {
        'serviceKey': service_key,
        'type': 'json',
        'inqryDiv': '1',  # 조회구분 (1: 입찰공고일시)
        'inqryBgnDt': (datetime.now() - timedelta(days=7)).strftime('%Y%m%d'),
        'inqryEndDt': datetime.now().strftime('%Y%m%d'),
        'numOfRows': '10',
        'pageNo': '1'
    }
    
    print("=" * 50)
    print("나라장터 API 연결 테스트")
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
                            print(f"조회된 공고 수: {len(items) if isinstance(items, list) else 1}")
                            
                            # 첫 번째 공고 정보 출력
                            first_item = items[0] if isinstance(items, list) else items
                            print("\n첫 번째 공고 정보:")
                            print(f"  - 공고번호: {first_item.get('bidNtceNo', 'N/A')}")
                            print(f"  - 공고명: {first_item.get('bidNtceNm', 'N/A')}")
                            print(f"  - 발주기관: {first_item.get('dminsttNm', 'N/A')}")
                        else:
                            print("조회된 공고가 없습니다.")
                    else:
                        print(f"⚠ API 응답 오류: {result_msg}")
                        
                        # 인증 오류인 경우 안내
                        if "SERVICE_KEY" in result_msg or "인증" in result_msg:
                            print("\n[해결 방법]")
                            print("1. 공공데이터포털(data.go.kr)에서 API 키를 발급받으세요")
                            print("2. 이 파일의 service_key 변수에 발급받은 키를 입력하세요")
                            print("3. API 사용 신청이 승인되었는지 확인하세요")
                else:
                    print("예상치 못한 응답 형식입니다.")
                    print(f"응답 내용: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
                    
            except json.JSONDecodeError as e:
                print(f"✗ JSON 파싱 실패: {e}")
                print(f"응답 내용 (처음 500자): {response.text[:500]}")
                
                # XML 응답일 가능성 확인
                if response.text.startswith('<?xml'):
                    print("\n응답이 XML 형식입니다. 'type=json' 파라미터를 확인하세요.")
                    
        elif response.status_code == 401:
            print("✗ 인증 실패 (401)")
            print("API 키가 올바른지 확인하세요.")
        elif response.status_code == 404:
            print("✗ API 엔드포인트를 찾을 수 없습니다 (404)")
            print("API URL이 올바른지 확인하세요.")
        else:
            print(f"✗ API 호출 실패: HTTP {response.status_code}")
            print(f"응답 내용: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print("✗ API 호출 시간 초과")
        print("네트워크 연결을 확인하거나 나중에 다시 시도하세요.")
    except requests.exceptions.ConnectionError as e:
        print(f"✗ 연결 오류: {e}")
        print("네트워크 연결을 확인하세요.")
    except Exception as e:
        print(f"✗ 예기치 않은 오류: {e}")
        
    print("=" * 50)
    print("\n[추가 테스트 방법]")
    print("1. service_key 변수에 실제 API 키를 입력하세요")
    print("2. 다시 실행: python3 test_api_connection.py")
    print("3. Flask 앱에서 테스트: http://localhost:5000 접속")

if __name__ == "__main__":
    test_narajangter_api()