#!/usr/bin/env python3
"""
데이터베이스 인덱스 추가 스크립트
성능 최적화를 위한 인덱스 생성
"""
import sqlite3
import os
from datetime import datetime

# 데이터베이스 경로
DB_PATH = '/home/ls/nara1/나라장터 api/narajangter_app/src/database/app.db'

def add_indexes():
    """데이터베이스에 인덱스 추가"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ 데이터베이스 파일이 없습니다: {DB_PATH}")
        return
    
    print("=" * 60)
    print("데이터베이스 인덱스 추가 작업 시작")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 추가할 인덱스 목록
    indexes = [
        # bid_notices 테이블 인덱스
        ("idx_bid_notice_no", "bid_notices", "bid_notice_no"),
        ("idx_bid_notice_ord", "bid_notices", "bid_notice_ord"),
        ("idx_rgst_dt", "bid_notices", "rgst_dt"),
        ("idx_dminstt_nm", "bid_notices", "dminstt_nm"),
        ("idx_work_div_nm", "bid_notices", "work_div_nm"),
        ("idx_bid_close_dt", "bid_notices", "bid_close_dt"),
        ("idx_openg_dt", "bid_notices", "openg_dt"),
        # 복합 인덱스
        ("idx_bid_notice_composite", "bid_notices", "bid_notice_no, bid_notice_ord"),
        
        # successful_bids 테이블 인덱스
        ("idx_sb_bid_notice_no", "successful_bids", "bid_notice_no"),
        ("idx_sb_openg_dt", "successful_bids", "openg_dt"),
        ("idx_sb_work_div_nm", "successful_bids", "work_div_nm"),
        ("idx_sb_scsbid_corp_nm", "successful_bids", "scsbid_corp_nm"),
        
        # api_configs 테이블 인덱스
        ("idx_api_config_active", "api_configs", "is_active")
    ]
    
    created_count = 0
    skipped_count = 0
    
    for index_name, table_name, columns in indexes:
        try:
            # 테이블 존재 확인
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if not cursor.fetchone():
                print(f"⚠️  테이블 {table_name}이 존재하지 않습니다. 건너뜁니다.")
                continue
            
            # 인덱스 생성
            sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({columns})"
            cursor.execute(sql)
            
            # 인덱스 생성 확인
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='index' AND name='{index_name}'")
            if cursor.fetchone():
                print(f"✅ 인덱스 생성/확인: {index_name} on {table_name}({columns})")
                created_count += 1
            else:
                print(f"⚠️  인덱스 생성 실패: {index_name}")
                skipped_count += 1
                
        except sqlite3.Error as e:
            print(f"❌ 오류 발생 ({index_name}): {e}")
            skipped_count += 1
    
    # 변경사항 커밋
    conn.commit()
    
    # 통계 정보 업데이트 (ANALYZE)
    print("\n통계 정보 업데이트 중...")
    cursor.execute("ANALYZE")
    conn.commit()
    
    # 데이터베이스 최적화 (VACUUM)
    print("데이터베이스 최적화 중...")
    cursor.execute("VACUUM")
    
    # 현재 인덱스 목록 확인
    print("\n" + "=" * 60)
    print("현재 데이터베이스 인덱스 목록")
    print("=" * 60)
    
    cursor.execute("""
        SELECT name, tbl_name, sql 
        FROM sqlite_master 
        WHERE type='index' 
        AND sql IS NOT NULL
        ORDER BY tbl_name, name
    """)
    
    indexes = cursor.fetchall()
    for idx_name, tbl_name, sql in indexes:
        print(f"📌 {tbl_name}.{idx_name}")
    
    # 테이블별 행 수 확인
    print("\n" + "=" * 60)
    print("테이블별 데이터 현황")
    print("=" * 60)
    
    tables = ['bid_notices', 'successful_bids', 'api_configs']
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"📊 {table}: {count:,}개 행")
        except:
            print(f"📊 {table}: 테이블 없음")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print(f"작업 완료: {created_count}개 인덱스 생성/확인, {skipped_count}개 건너뜀")
    print("=" * 60)

if __name__ == "__main__":
    add_indexes()