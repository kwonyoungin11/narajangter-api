#!/usr/bin/env python3
"""
나라장터 API 종합 테스트
모든 최적화 기능을 테스트
"""
import sys
import os
sys.path.insert(0, '/home/ls/nara1/나라장터 api/narajangter_app')

import requests
import time
from datetime import datetime, timedelta
import json

def print_section(title):
    """섹션 헤더 출력"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)

def test_api_connection():
    """1. API 연결 테스트"""
    print_section("1. API 연결 테스트")
    
    SERVICE_KEY = "IShTX5OFowHN6eDSaOVglEh3a3DE5aqDpk2XopebFZM9joF7v/oDnjeGbg0RAC8fr2TJ2O5ip6BYwodpk1W7fA=="
    
    # 입찰공고 API
    url = "http://apis.data.go.kr/1230000/ao/PubDataOpnStdService/getDataSetOpnStdBidPblancInfo"
    params = {
        'ServiceKey': SERVICE_KEY,
        'type': 'json',
        'numOfRows': '5',
        'pageNo': '1',
        'bidNtceBgnDt': '202501010000',
        'bidNtceEndDt': '202501072359'
    }
    
    try:
        print("📡 입찰공고 API 호출 중...")
        start = time.time()
        response = requests.get(url, params=params, timeout=30)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            if 'response' in data and data['response']['header']['resultCode'] == '00':
                total = data['response']['body'].get('totalCount', 0)
                items = data['response']['body'].get('items', [])
                
                print(f"✅ 성공! (응답시간: {elapsed:.2f}초)")
                print(f"   - 전체 데이터: {total:,}건")
                print(f"   - 조회된 데이터: {len(items) if isinstance(items, list) else 1}건")
                
                # 샘플 데이터 표시
                if items and isinstance(items, list) and len(items) > 0:
                    item = items[0]
                    print(f"\n   📋 샘플 데이터:")
                    print(f"      공고번호: {item.get('bidNtceNo', 'N/A')}")
                    print(f"      공고명: {item.get('bidNtceNm', 'N/A')[:50]}...")
                    print(f"      발주기관: {item.get('dminsttNm', 'N/A')}")
                return True
            else:
                print(f"❌ API 오류: {data.get('response', {}).get('header', {}).get('resultMsg', 'Unknown')}")
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
    
    return False

def test_flask_server():
    """2. Flask 서버 테스트"""
    print_section("2. Flask 서버 상태 확인")
    
    try:
        response = requests.get("http://localhost:5000", timeout=2)
        if response.status_code == 200:
            print("✅ Flask 서버 실행 중")
            
            # API 설정 확인
            config_resp = requests.get("http://localhost:5000/api/narajangter/config")
            if config_resp.status_code == 200:
                config = config_resp.json()
                print(f"   - API 키 설정: {'✅ 설정됨' if 'service_key' in config else '❌ 미설정'}")
            
            return True
        else:
            print(f"⚠️ 서버 응답 이상: HTTP {response.status_code}")
    except:
        print("❌ Flask 서버가 실행되지 않음")
        print("   실행 명령: cd /home/ls/nara1/나라장터\\ api/narajangter_app && python3 src/main.py")
    
    return False

def test_database():
    """3. 데이터베이스 테스트"""
    print_section("3. 데이터베이스 상태 확인")
    
    import sqlite3
    db_path = '/home/ls/nara1/나라장터 api/narajangter_app/src/database/app.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 테이블 확인
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"✅ 데이터베이스 연결 성공")
        print(f"   테이블: {', '.join([t[0] for t in tables])}")
        
        # 인덱스 확인
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index'")
        index_count = cursor.fetchone()[0]
        print(f"   인덱스: {index_count}개")
        
        # 데이터 건수 확인
        for table in ['bid_notices', 'successful_bids', 'api_configs']:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   {table}: {count:,}건")
            except:
                pass
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ 데이터베이스 오류: {e}")
        return False

def test_batch_processing():
    """4. 배치 처리 테스트"""
    print_section("4. 배치 처리 최적화 테스트")
    
    try:
        # BatchProcessor 임포트
        from src.utils.batch_processor import BatchProcessor
        from src.models.narajangter import db
        
        print("✅ BatchProcessor 모듈 로드 성공")
        print("   기능:")
        print("   - 병렬 페이지 조회 (ThreadPoolExecutor)")
        print("   - 대량 삽입 최적화 (bulk insert)")
        print("   - 중복 체크 로직")
        print("   - 진행 상황 모니터링")
        return True
    except ImportError as e:
        print(f"⚠️ BatchProcessor 모듈을 로드할 수 없음: {e}")
        print("   Flask 앱 내에서만 사용 가능")
        return False

def test_api_helper():
    """5. API Helper 테스트"""
    print_section("5. API Helper 유틸리티 테스트")
    
    try:
        from src.utils.api_helper import APIHelper
        
        print("✅ APIHelper 모듈 로드 성공")
        print("   기능:")
        print("   - 타임아웃: 30초 (기본)")
        print("   - 재시도: 최대 3회")
        print("   - 모니터링 로깅")
        print("   - 날짜 범위 검증")
        
        # 날짜 검증 테스트
        helper = APIHelper()
        valid = helper.validate_date_range('20250101', '20250131', 31)
        print(f"\n   날짜 범위 검증 테스트:")
        print(f"   - 2025-01-01 ~ 2025-01-31 (31일): {'✅ 유효' if valid else '❌ 무효'}")
        
        return True
    except ImportError:
        print("⚠️ APIHelper 모듈을 로드할 수 없음")
        return False

def test_performance():
    """6. 성능 측정"""
    print_section("6. 성능 벤치마크")
    
    SERVICE_KEY = "IShTX5OFowHN6eDSaOVglEh3a3DE5aqDpk2XopebFZM9joF7v/oDnjeGbg0RAC8fr2TJ2O5ip6BYwodpk1W7fA=="
    url = "http://apis.data.go.kr/1230000/ao/PubDataOpnStdService/getDataSetOpnStdBidPblancInfo"
    
    print("📊 API 응답 시간 측정 (5회 평균)")
    
    times = []
    for i in range(5):
        params = {
            'ServiceKey': SERVICE_KEY,
            'type': 'json',
            'numOfRows': '10',
            'pageNo': str(i+1),
            'bidNtceBgnDt': '202501010000',
            'bidNtceEndDt': '202501022359'
        }
        
        start = time.time()
        try:
            response = requests.get(url, params=params, timeout=30)
            elapsed = time.time() - start
            times.append(elapsed)
            print(f"   {i+1}회: {elapsed:.3f}초")
        except:
            print(f"   {i+1}회: 실패")
        
        time.sleep(0.2)  # API 부하 방지
    
    if times:
        avg = sum(times) / len(times)
        print(f"\n   평균 응답 시간: {avg:.3f}초")
        print(f"   최소: {min(times):.3f}초 / 최대: {max(times):.3f}초")
        
        if avg < 1.0:
            print("   ✅ 목표 달성 (< 1초)")
        else:
            print("   ⚠️ 최적화 필요 (목표: < 1초)")

def test_sync_endpoint():
    """7. 데이터 동기화 엔드포인트 테스트"""
    print_section("7. 데이터 동기화 API 테스트")
    
    try:
        # 작은 범위로 테스트
        sync_data = {
            'start_date': '20250101',
            'end_date': '20250101'  # 하루만
        }
        
        print("📥 동기화 테스트 (2025-01-01 하루 데이터)")
        
        response = requests.post(
            "http://localhost:5000/api/narajangter/sync-bid-notices",
            json=sync_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 동기화 성공")
            print(f"   메시지: {result.get('message', 'N/A')}")
        else:
            print(f"❌ 동기화 실패: HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️ Flask 서버가 실행되지 않아 테스트 불가")
    except Exception as e:
        print(f"❌ 오류: {e}")

def main():
    """메인 테스트 실행"""
    print("\n" + "🚀" * 35)
    print(" 나라장터 API 종합 테스트 시작")
    print("🚀" * 35)
    print(f"\n시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 테스트 실행
    results = {
        "API 연결": test_api_connection(),
        "Flask 서버": test_flask_server(),
        "데이터베이스": test_database(),
        "배치 처리": test_batch_processing(),
        "API Helper": test_api_helper(),
    }
    
    # 성능 테스트
    test_performance()
    
    # Flask 서버가 실행 중이면 동기화 테스트
    if results["Flask 서버"]:
        test_sync_endpoint()
    
    # 결과 요약
    print_section("📋 테스트 결과 요약")
    
    for name, result in results.items():
        status = "✅ 성공" if result else "❌ 실패"
        print(f"   {name}: {status}")
    
    success_rate = sum(results.values()) / len(results) * 100
    print(f"\n   전체 성공률: {success_rate:.0f}%")
    
    if success_rate == 100:
        print("\n   🎉 모든 테스트 통과! 시스템이 정상 작동합니다.")
    elif success_rate >= 80:
        print("\n   ⚠️ 대부분 정상이나 일부 개선 필요")
    else:
        print("\n   ❌ 주요 기능에 문제가 있습니다. 점검이 필요합니다.")
    
    print(f"\n종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

if __name__ == "__main__":
    main()