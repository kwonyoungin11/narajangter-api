"""
배치 처리 최적화 모듈
대용량 데이터 동기화를 위한 효율적인 처리
"""
import requests
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import concurrent.futures
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatchProcessor:
    """배치 처리 최적화 클래스"""
    
    def __init__(self, db, service_key: str):
        self.db = db
        self.service_key = service_key
        self.api_call_count = 0
        self.start_time = time.time()
    
    def fetch_page(self, url: str, params: Dict, page_no: int) -> Optional[Dict]:
        """단일 페이지 데이터 조회"""
        params_copy = params.copy()
        params_copy['pageNo'] = str(page_no)
        
        try:
            response = requests.get(url, params=params_copy, timeout=30)
            self.api_call_count += 1
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'response' in data and data['response']['header']['resultCode'] == '00':
                        return data['response']['body']
                except:
                    logger.error(f"Page {page_no}: JSON 파싱 실패")
            else:
                logger.error(f"Page {page_no}: HTTP {response.status_code}")
        except Exception as e:
            logger.error(f"Page {page_no}: {e}")
        
        return None
    
    def fetch_all_pages_parallel(
        self, 
        url: str, 
        params: Dict, 
        max_workers: int = 5,
        max_pages: int = None
    ) -> List[Dict]:
        """병렬로 모든 페이지 데이터 조회"""
        
        # 첫 페이지로 전체 건수 확인
        first_page = self.fetch_page(url, params, 1)
        if not first_page:
            return []
        
        total_count = first_page.get('totalCount', 0)
        num_rows = int(params.get('numOfRows', 100))
        total_pages = (total_count + num_rows - 1) // num_rows
        
        if max_pages:
            total_pages = min(total_pages, max_pages)
        
        logger.info(f"전체 {total_count}건, {total_pages}페이지 조회 시작")
        
        all_items = []
        
        # 첫 페이지 데이터 추가
        items = first_page.get('items', [])
        if isinstance(items, list):
            all_items.extend(items)
        elif items:
            all_items.append(items)
        
        # 나머지 페이지 병렬 조회
        if total_pages > 1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self.fetch_page, url, params, page): page 
                    for page in range(2, total_pages + 1)
                }
                
                for future in concurrent.futures.as_completed(futures):
                    page_no = futures[future]
                    try:
                        result = future.result()
                        if result:
                            items = result.get('items', [])
                            if isinstance(items, list):
                                all_items.extend(items)
                            elif items:
                                all_items.append(items)
                            
                            # 진행 상황 로깅
                            if len(all_items) % 500 == 0:
                                logger.info(f"진행: {len(all_items)}/{total_count}건 조회 완료")
                    except Exception as e:
                        logger.error(f"Page {page_no} 처리 오류: {e}")
        
        logger.info(f"조회 완료: 총 {len(all_items)}건")
        return all_items
    
    def bulk_insert_bid_notices(self, items: List[Dict]) -> int:
        """입찰공고 대량 삽입 (중복 체크 포함)"""
        
        if not items:
            return 0
        
        # 기존 데이터의 bid_notice_no 조회
        existing_query = text("""
            SELECT bid_notice_no, bid_notice_ord 
            FROM bid_notices
        """)
        
        existing_records = self.db.session.execute(existing_query).fetchall()
        existing_keys = {(row[0], row[1]) for row in existing_records}
        
        # 새로운 데이터 준비
        new_records = []
        update_records = []
        
        for item in items:
            key = (item.get('bidNtceNo'), item.get('bidNtceOrd', '00'))
            
            record = {
                'bid_notice_no': item.get('bidNtceNo'),
                'bid_notice_nm': item.get('bidNtceNm', '')[:500],
                'bid_notice_ord': item.get('bidNtceOrd', '00'),
                'dminstt_nm': item.get('dminsttNm', '')[:200],
                'rgst_dt': self._parse_datetime(item.get('rgstDt')),
                'bid_begin_dt': self._parse_datetime(item.get('bidBeginDt')),
                'bid_close_dt': self._parse_datetime(item.get('bidClseDt')),
                'openg_dt': self._parse_datetime(item.get('opengDt')),
                'presmpt_price': self._parse_int(item.get('presmptPrce')),
                'basic_amount': self._parse_int(item.get('asignBdgtAmt')),
                'bid_method_nm': item.get('bidMethdNm', '')[:100],
                'cntrct_cncls_mthd_nm': item.get('cntrctCnclsMthdNm', '')[:100],
                'work_div_nm': item.get('taskClsfcNm', '')[:50],
                'created_at': datetime.utcnow()
            }
            
            if key not in existing_keys:
                new_records.append(record)
            else:
                # 업데이트 로직 (필요시)
                pass
        
        # 대량 삽입
        inserted_count = 0
        if new_records:
            try:
                # 배치 단위로 삽입 (SQLite는 한 번에 999개 제한)
                batch_size = 500
                for i in range(0, len(new_records), batch_size):
                    batch = new_records[i:i + batch_size]
                    
                    insert_query = text("""
                        INSERT INTO bid_notices (
                            bid_notice_no, bid_notice_nm, bid_notice_ord, dminstt_nm,
                            rgst_dt, bid_begin_dt, bid_close_dt, openg_dt,
                            presmpt_price, basic_amount, bid_method_nm,
                            cntrct_cncls_mthd_nm, work_div_nm, created_at
                        ) VALUES (
                            :bid_notice_no, :bid_notice_nm, :bid_notice_ord, :dminstt_nm,
                            :rgst_dt, :bid_begin_dt, :bid_close_dt, :openg_dt,
                            :presmpt_price, :basic_amount, :bid_method_nm,
                            :cntrct_cncls_mthd_nm, :work_div_nm, :created_at
                        )
                    """)
                    
                    self.db.session.execute(insert_query, batch)
                    inserted_count += len(batch)
                    
                    if inserted_count % 1000 == 0:
                        logger.info(f"삽입 진행: {inserted_count}건")
                
                self.db.session.commit()
                logger.info(f"✅ {inserted_count}건 신규 삽입 완료")
                
            except Exception as e:
                self.db.session.rollback()
                logger.error(f"대량 삽입 실패: {e}")
                raise
        
        return inserted_count
    
    def sync_bid_notices_optimized(
        self,
        start_date: str,
        end_date: str,
        max_pages: int = None
    ) -> Dict[str, Any]:
        """최적화된 입찰공고 동기화"""
        
        url = "http://apis.data.go.kr/1230000/ao/PubDataOpnStdService/getDataSetOpnStdBidPblancInfo"
        
        params = {
            'ServiceKey': self.service_key,
            'type': 'json',
            'bidNtceBgnDt': start_date + '0000',
            'bidNtceEndDt': end_date + '2359',
            'numOfRows': '100'
        }
        
        logger.info(f"동기화 시작: {start_date} ~ {end_date}")
        
        # 병렬로 모든 페이지 조회
        all_items = self.fetch_all_pages_parallel(url, params, max_pages=max_pages)
        
        # 대량 삽입
        inserted_count = self.bulk_insert_bid_notices(all_items)
        
        # 통계
        elapsed_time = time.time() - self.start_time
        
        result = {
            'success': True,
            'total_fetched': len(all_items),
            'inserted': inserted_count,
            'duplicates': len(all_items) - inserted_count,
            'api_calls': self.api_call_count,
            'elapsed_time': round(elapsed_time, 2),
            'items_per_second': round(len(all_items) / elapsed_time, 2) if elapsed_time > 0 else 0
        }
        
        logger.info(f"동기화 완료: {result}")
        return result
    
    def _parse_datetime(self, date_str: str) -> Optional[datetime]:
        """날짜 문자열 파싱"""
        if not date_str:
            return None
        try:
            if len(date_str) == 12:
                return datetime.strptime(date_str, '%Y%m%d%H%M')
            elif len(date_str) == 8:
                return datetime.strptime(date_str, '%Y%m%d')
        except:
            pass
        return None
    
    def _parse_int(self, value: Any) -> Optional[int]:
        """정수 파싱"""
        if value is None:
            return None
        try:
            return int(value)
        except:
            return None