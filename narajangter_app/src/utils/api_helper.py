"""
API 호출 헬퍼 유틸리티
타임아웃, 재시도, 모니터링 기능 포함
"""
import requests
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class APIHelper:
    """API 호출 헬퍼 클래스"""
    
    DEFAULT_TIMEOUT = 30  # 기본 타임아웃 30초
    MAX_RETRIES = 3      # 최대 재시도 횟수
    RETRY_DELAY = 2      # 재시도 간격 (초)
    
    @staticmethod
    def call_api(
        url: str,
        params: Dict[str, Any],
        method: str = 'GET',
        timeout: int = None,
        retry: bool = True
    ) -> Optional[requests.Response]:
        """
        API 호출 with 모니터링 및 재시도
        
        Args:
            url: API 엔드포인트 URL
            params: 요청 파라미터
            method: HTTP 메소드
            timeout: 타임아웃 (초)
            retry: 재시도 여부
        
        Returns:
            Response 객체 또는 None
        """
        timeout = timeout or APIHelper.DEFAULT_TIMEOUT
        max_retries = APIHelper.MAX_RETRIES if retry else 1
        
        for attempt in range(max_retries):
            start_time = time.time()
            
            try:
                # API 호출
                if method.upper() == 'GET':
                    response = requests.get(url, params=params, timeout=timeout)
                elif method.upper() == 'POST':
                    response = requests.post(url, json=params, timeout=timeout)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                # 응답 시간 계산
                elapsed_time = time.time() - start_time
                
                # 모니터링 로그
                logger.info(f"API Call Success - URL: {url}")
                logger.info(f"  Response Time: {elapsed_time:.2f}s")
                logger.info(f"  Status Code: {response.status_code}")
                logger.info(f"  Data Size: {len(response.content)} bytes")
                
                # 성공 응답 체크
                if response.status_code == 200:
                    return response
                else:
                    logger.warning(f"API returned non-200 status: {response.status_code}")
                    
                    # 5xx 에러는 재시도
                    if response.status_code >= 500 and attempt < max_retries - 1:
                        logger.info(f"Retrying after {APIHelper.RETRY_DELAY}s... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(APIHelper.RETRY_DELAY)
                        continue
                    
                    return response
                    
            except requests.exceptions.Timeout:
                elapsed_time = time.time() - start_time
                logger.error(f"API Timeout - URL: {url}, Timeout: {timeout}s, Elapsed: {elapsed_time:.2f}s")
                
                if attempt < max_retries - 1:
                    logger.info(f"Retrying after timeout... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(APIHelper.RETRY_DELAY)
                    continue
                    
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection Error - URL: {url}, Error: {e}")
                
                if attempt < max_retries - 1:
                    logger.info(f"Retrying after connection error... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(APIHelper.RETRY_DELAY)
                    continue
                    
            except Exception as e:
                logger.error(f"Unexpected Error - URL: {url}, Error: {e}")
                break
        
        logger.error(f"API call failed after {max_retries} attempts")
        return None
    
    @staticmethod
    def parse_api_response(response: requests.Response) -> Dict[str, Any]:
        """
        API 응답 파싱 with 에러 핸들링
        
        Args:
            response: Response 객체
        
        Returns:
            파싱된 데이터 딕셔너리
        """
        result = {
            'success': False,
            'data': None,
            'error': None,
            'total_count': 0,
            'items': []
        }
        
        if not response:
            result['error'] = "No response received"
            return result
        
        try:
            # JSON 파싱 시도
            data = response.json()
            
            # 공공데이터 표준 응답 형식 체크
            if 'response' in data:
                header = data.get('response', {}).get('header', {})
                body = data.get('response', {}).get('body', {})
                
                result_code = header.get('resultCode')
                result_msg = header.get('resultMsg')
                
                if result_code == '00':
                    # 성공
                    result['success'] = True
                    result['data'] = body
                    result['total_count'] = body.get('totalCount', 0)
                    
                    items = body.get('items', [])
                    if isinstance(items, list):
                        result['items'] = items
                    elif items:  # 단일 객체인 경우
                        result['items'] = [items]
                else:
                    # API 에러
                    result['error'] = f"API Error ({result_code}): {result_msg}"
                    logger.error(result['error'])
            else:
                # 비표준 응답
                result['data'] = data
                result['success'] = True
                
        except ValueError as e:
            # JSON 파싱 실패 - XML 응답일 가능성
            result['error'] = f"JSON parsing failed: {e}"
            
            # XML 응답 체크
            if response.text.startswith('<?xml'):
                result['error'] += " (Response is XML format)"
                # XML 파싱 로직 추가 가능
            
            logger.error(result['error'])
            
        except Exception as e:
            result['error'] = f"Unexpected error: {e}"
            logger.error(result['error'])
        
        return result
    
    @staticmethod
    def validate_date_range(start_date: str, end_date: str, max_days: int = 31) -> bool:
        """
        날짜 범위 검증
        
        Args:
            start_date: 시작일 (YYYYMMDD)
            end_date: 종료일 (YYYYMMDD)
            max_days: 최대 허용 일수
        
        Returns:
            유효 여부
        """
        try:
            start = datetime.strptime(start_date[:8], '%Y%m%d')
            end = datetime.strptime(end_date[:8], '%Y%m%d')
            
            diff = (end - start).days
            
            if diff < 0:
                logger.error("End date is before start date")
                return False
            
            if diff > max_days:
                logger.error(f"Date range exceeds maximum {max_days} days: {diff} days")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Date validation error: {e}")
            return False