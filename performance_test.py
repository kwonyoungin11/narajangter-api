#!/usr/bin/env python3
"""
나라장터 API 성능 테스트 스크립트
"""
import time
import requests
import statistics
from datetime import datetime
import concurrent.futures
import json

def measure_api_response_time(url, params, iterations=10):
    """API 응답 시간 측정"""
    response_times = []
    success_count = 0
    
    print(f"\n{'='*60}")
    print(f"API 응답 시간 측정 ({iterations}회)")
    print(f"{'='*60}")
    
    for i in range(iterations):
        start_time = time.time()
        
        try:
            response = requests.get(url, params=params, timeout=30)
            elapsed = time.time() - start_time
            response_times.append(elapsed)
            
            if response.status_code == 200:
                success_count += 1
                print(f"  {i+1}. ✅ {elapsed:.2f}s")
            else:
                print(f"  {i+1}. ❌ {elapsed:.2f}s (HTTP {response.status_code})")
        except Exception as e:
            print(f"  {i+1}. ❌ 오류: {e}")
        
        # 부하 분산을 위한 짧은 대기
        time.sleep(0.5)
    
    if response_times:
        print(f"\n📊 통계:")
        print(f"  - 성공률: {success_count}/{iterations} ({success_count/iterations*100:.1f}%)")
        print(f"  - 평균 응답 시간: {statistics.mean(response_times):.2f}s")
        print(f"  - 최소 응답 시간: {min(response_times):.2f}s")
        print(f"  - 최대 응답 시간: {max(response_times):.2f}s")
        if len(response_times) > 1:
            print(f"  - 표준편차: {statistics.stdev(response_times):.2f}s")
    
    return response_times

def concurrent_api_test(url, params, concurrent_users=5, requests_per_user=3):
    """동시 접속 테스트"""
    print(f"\n{'='*60}")
    print(f"동시 접속 테스트 (사용자: {concurrent_users}, 요청/사용자: {requests_per_user})")
    print(f"{'='*60}")
    
    def make_request(user_id, request_id):
        start_time = time.time()
        try:
            response = requests.get(url, params=params, timeout=30)
            elapsed = time.time() - start_time
            return {
                'user_id': user_id,
                'request_id': request_id,
                'success': response.status_code == 200,
                'elapsed': elapsed,
                'status_code': response.status_code
            }
        except Exception as e:
            return {
                'user_id': user_id,
                'request_id': request_id,
                'success': False,
                'elapsed': time.time() - start_time,
                'error': str(e)
            }
    
    all_results = []
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        futures = []
        for user_id in range(concurrent_users):
            for request_id in range(requests_per_user):
                futures.append(
                    executor.submit(make_request, user_id, request_id)
                )
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            all_results.append(result)
            
            status = "✅" if result['success'] else "❌"
            print(f"  User {result['user_id']}, Request {result['request_id']}: "
                  f"{status} {result['elapsed']:.2f}s")
    
    total_time = time.time() - start_time
    success_count = sum(1 for r in all_results if r['success'])
    total_requests = len(all_results)
    
    print(f"\n📊 동시 접속 테스트 결과:")
    print(f"  - 전체 소요 시간: {total_time:.2f}s")
    print(f"  - 총 요청 수: {total_requests}")
    print(f"  - 성공률: {success_count}/{total_requests} ({success_count/total_requests*100:.1f}%)")
    print(f"  - 처리량: {total_requests/total_time:.2f} req/s")
    
    response_times = [r['elapsed'] for r in all_results]
    if response_times:
        print(f"  - 평균 응답 시간: {statistics.mean(response_times):.2f}s")
        print(f"  - 최소 응답 시간: {min(response_times):.2f}s")
        print(f"  - 최대 응답 시간: {max(response_times):.2f}s")

def test_flask_endpoints():
    """Flask 애플리케이션 엔드포인트 테스트"""
    base_url = "http://localhost:5000"
    
    print(f"\n{'='*60}")
    print("Flask 애플리케이션 엔드포인트 테스트")
    print(f"{'='*60}")
    
    endpoints = [
        ("/api/narajangter/config", "GET", None),
        ("/api/narajangter/bid-notices?page=1&per_page=10", "GET", None),
        ("/api/narajangter/successful-bids?page=1&per_page=10", "GET", None),
        ("/api/narajangter/analytics/bid-amount", "GET", None),
    ]
    
    for endpoint, method, data in endpoints:
        url = base_url + endpoint
        print(f"\n테스트: {method} {endpoint}")
        
        start_time = time.time()
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            else:
                response = requests.post(url, json=data, timeout=10)
            
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                print(f"  ✅ 성공 ({elapsed:.2f}s)")
                try:
                    data = response.json()
                    if 'items' in data:
                        print(f"     데이터: {len(data['items'])}건")
                    elif 'total' in data:
                        print(f"     전체: {data['total']}건")
                except:
                    pass
            else:
                print(f"  ❌ 실패 ({elapsed:.2f}s) - HTTP {response.status_code}")
        except Exception as e:
            print(f"  ❌ 오류: {e}")

def main():
    """메인 테스트 실행"""
    print("=" * 70)
    print("나라장터 API 성능 테스트")
    print("=" * 70)
    print(f"테스트 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # API 키
    SERVICE_KEY = "IShTX5OFowHN6eDSaOVglEh3a3DE5aqDpk2XopebFZM9joF7v/oDnjeGbg0RAC8fr2TJ2O5ip6BYwodpk1W7fA=="
    
    # 테스트할 API
    api_url = "http://apis.data.go.kr/1230000/ao/PubDataOpnStdService/getDataSetOpnStdBidPblancInfo"
    params = {
        'ServiceKey': SERVICE_KEY,
        'type': 'json',
        'numOfRows': '10',
        'pageNo': '1',
        'bidNtceBgnDt': '202501010000',
        'bidNtceEndDt': '202501012359'
    }
    
    # 1. API 응답 시간 측정
    response_times = measure_api_response_time(api_url, params, iterations=5)
    
    # 2. 동시 접속 테스트
    concurrent_api_test(api_url, params, concurrent_users=3, requests_per_user=2)
    
    # 3. Flask 엔드포인트 테스트 (서버가 실행 중인 경우)
    try:
        response = requests.get("http://localhost:5000", timeout=1)
        test_flask_endpoints()
    except:
        print("\n⚠️ Flask 서버가 실행되지 않아 엔드포인트 테스트를 건너뜁니다.")
    
    print(f"\n테스트 완료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

if __name__ == "__main__":
    main()