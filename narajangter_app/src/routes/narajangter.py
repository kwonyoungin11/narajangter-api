from flask import Blueprint, request, jsonify
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from src.models.narajangter import db, BidNotice, SuccessfulBid, ApiConfig
from urllib.parse import quote

narajangter_bp = Blueprint('narajangter', __name__)

# 나라장터 API 기본 URL (공공데이터개방표준서비스 - 최신 버전)
BID_NOTICE_API_URL = "http://apis.data.go.kr/1230000/ao/PubDataOpnStdService/getDataSetOpnStdBidPblancInfo"
SUCCESSFUL_BID_API_URL = "http://apis.data.go.kr/1230000/ao/PubDataOpnStdService/getDataSetOpnStdScsbidInfo"

def get_active_service_key():
    """활성화된 서비스 키 조회"""
    config = ApiConfig.query.filter_by(is_active=True).first()
    return config.service_key if config else None

def parse_datetime(date_str):
    """날짜 문자열을 datetime 객체로 변환"""
    if not date_str:
        return None
    try:
        # YYYYMMDDHHMM 형식
        if len(date_str) == 12:
            return datetime.strptime(date_str, '%Y%m%d%H%M')
        # YYYYMMDD 형식
        elif len(date_str) == 8:
            return datetime.strptime(date_str, '%Y%m%d')
        else:
            return None
    except ValueError:
        return None

@narajangter_bp.route('/config', methods=['POST'])
def set_api_config():
    """API 설정 저장"""
    try:
        data = request.get_json()
        service_key = data.get('service_key')
        
        if not service_key:
            return jsonify({'error': '서비스 키가 필요합니다.'}), 400
        
        # 기존 설정 비활성화
        ApiConfig.query.update({'is_active': False})
        
        # 새 설정 추가
        new_config = ApiConfig(service_key=service_key, is_active=True)
        db.session.add(new_config)
        db.session.commit()
        
        return jsonify({'message': 'API 설정이 저장되었습니다.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@narajangter_bp.route('/config', methods=['GET'])
def get_api_config():
    """API 설정 조회"""
    try:
        config = ApiConfig.query.filter_by(is_active=True).first()
        if config:
            return jsonify(config.to_dict()), 200
        else:
            return jsonify({'message': '설정된 API 키가 없습니다.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@narajangter_bp.route('/bid-notices', methods=['GET'])
def get_bid_notices():
    """입찰공고 목록 조회"""
    try:
        # 쿼리 파라미터
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search_keyword = request.args.get('search', '')
        dminstt_nm = request.args.get('dminstt_nm', '')  # 발주처 검색
        work_div = request.args.get('work_div', '')  # 업무구분
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        # 기본 쿼리
        query = BidNotice.query
        
        # 검색 조건 적용
        if search_keyword:
            query = query.filter(BidNotice.bid_notice_nm.contains(search_keyword))
        
        if dminstt_nm:
            query = query.filter(BidNotice.dminstt_nm.contains(dminstt_nm))
        
        if work_div:
            query = query.filter(BidNotice.work_div_nm == work_div)
        
        if start_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(BidNotice.rgst_dt >= start_dt)
        
        if end_date:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(BidNotice.rgst_dt <= end_dt)
        
        # 페이지네이션
        pagination = query.order_by(BidNotice.rgst_dt.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'items': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@narajangter_bp.route('/successful-bids', methods=['GET'])
def get_successful_bids():
    """낙찰정보 목록 조회"""
    try:
        # 쿼리 파라미터
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search_keyword = request.args.get('search', '')
        work_div = request.args.get('work_div', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        # 기본 쿼리
        query = SuccessfulBid.query
        
        # 검색 조건 적용
        if search_keyword:
            query = query.filter(SuccessfulBid.scsbid_corp_nm.contains(search_keyword))
        
        if work_div:
            query = query.filter(SuccessfulBid.work_div_nm == work_div)
        
        if start_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(SuccessfulBid.openg_dt >= start_dt)
        
        if end_date:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(SuccessfulBid.openg_dt <= end_dt)
        
        # 페이지네이션
        pagination = query.order_by(SuccessfulBid.openg_dt.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'items': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@narajangter_bp.route('/sync-bid-notices', methods=['POST'])
def sync_bid_notices():
    """나라장터 API에서 입찰공고 데이터 동기화"""
    try:
        service_key = get_active_service_key()
        if not service_key:
            return jsonify({'error': 'API 서비스 키가 설정되지 않았습니다.'}), 400
        
        data = request.get_json()
        start_date = data.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y%m%d'))
        end_date = data.get('end_date', datetime.now().strftime('%Y%m%d'))
        
        # API 호출 파라미터
        params = {
            'serviceKey': service_key,
            'type': 'json',
            'bidNtceBgnDt': start_date + '0000',  # YYYYMMDDHHMM 형식
            'bidNtceEndDt': end_date + '2359',  # YYYYMMDDHHMM 형식
            'numOfRows': '100',
            'pageNo': '1'
        }
        
        response = requests.get(BID_NOTICE_API_URL, params=params)
        
        if response.status_code == 200:
            try:
                data = response.json()
                items = data.get('response', {}).get('body', {}).get('items', [])
                
                if not isinstance(items, list):
                    items = [items] if items else []
                
                synced_count = 0
                for item in items:
                    # 중복 체크
                    existing = BidNotice.query.filter_by(
                        bid_notice_no=item.get('bidNtceNo'),
                        bid_notice_ord=item.get('bidNtceOrd')
                    ).first()
                    
                    if not existing:
                        try:
                            bid_notice = BidNotice(
                                bid_notice_no=item.get('bidNtceNo'),
                                bid_notice_nm=item.get('bidNtceNm'),
                                bid_notice_ord=item.get('bidNtceOrd', '00'),
                                dminstt_nm=item.get('dminsttNm'),
                                rgst_dt=parse_datetime(item.get('rgstDt')),
                                bid_begin_dt=parse_datetime(item.get('bidBeginDt')),
                                bid_close_dt=parse_datetime(item.get('bidClseDt')),
                                openg_dt=parse_datetime(item.get('opengDt')),
                                presmpt_price=int(item.get('presmptPrce', 0)) if item.get('presmptPrce') else None,
                                basic_amount=int(item.get('asignBdgtAmt', 0)) if item.get('asignBdgtAmt') else None,
                                bid_method_nm=item.get('bidMethdNm'),
                                cntrct_cncls_mthd_nm=item.get('cntrctCnclsMthdNm'),
                                work_div_nm=item.get('taskClsfcNm')
                            )
                            db.session.add(bid_notice)
                            db.session.flush()  # 즉시 플러시하여 중복 체크
                            synced_count += 1
                        except Exception as e:
                            db.session.rollback()
                            # 중복이면 건너뛰기
                            continue
                
                db.session.commit()
                return jsonify({'message': f'{synced_count}건의 입찰공고가 동기화되었습니다.'}), 200
                
            except ValueError as e:
                return jsonify({'error': f'JSON 파싱 오류: {str(e)}'}), 500
        else:
            return jsonify({'error': f'API 호출 실패: {response.status_code}'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@narajangter_bp.route('/analytics/bid-amount', methods=['GET'])
def get_bid_amount_analytics():
    """입찰금액 분석 데이터"""
    try:
        # 업무구분별 평균 추정가격
        work_div_stats = db.session.query(
            BidNotice.work_div_nm,
            db.func.count(BidNotice.id).label('count'),
            db.func.avg(BidNotice.presmpt_price).label('avg_price'),
            db.func.sum(BidNotice.presmpt_price).label('total_price')
        ).filter(
            BidNotice.presmpt_price.isnot(None)
        ).group_by(BidNotice.work_div_nm).all()
        
        # 월별 입찰공고 건수 및 금액
        monthly_stats = db.session.query(
            db.func.strftime('%Y-%m', BidNotice.rgst_dt).label('month'),
            db.func.count(BidNotice.id).label('count'),
            db.func.sum(BidNotice.presmpt_price).label('total_amount')
        ).filter(
            BidNotice.rgst_dt.isnot(None),
            BidNotice.presmpt_price.isnot(None)
        ).group_by(
            db.func.strftime('%Y-%m', BidNotice.rgst_dt)
        ).order_by('month').all()
        
        return jsonify({
            'work_div_stats': [
                {
                    'work_div_nm': stat.work_div_nm,
                    'count': stat.count,
                    'avg_price': float(stat.avg_price) if stat.avg_price else 0,
                    'total_price': float(stat.total_price) if stat.total_price else 0
                }
                for stat in work_div_stats
            ],
            'monthly_stats': [
                {
                    'month': stat.month,
                    'count': stat.count,
                    'total_amount': float(stat.total_amount) if stat.total_amount else 0
                }
                for stat in monthly_stats
            ]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@narajangter_bp.route('/analytics/successful-bid-rate', methods=['GET'])
def get_successful_bid_rate_analytics():
    """낙찰률 분석 데이터"""
    try:
        # 업무구분별 평균 낙찰률
        rate_stats = db.session.query(
            SuccessfulBid.work_div_nm,
            db.func.count(SuccessfulBid.id).label('count'),
            db.func.avg(SuccessfulBid.scsbid_rate).label('avg_rate'),
            db.func.min(SuccessfulBid.scsbid_rate).label('min_rate'),
            db.func.max(SuccessfulBid.scsbid_rate).label('max_rate')
        ).filter(
            SuccessfulBid.scsbid_rate.isnot(None)
        ).group_by(SuccessfulBid.work_div_nm).all()
        
        return jsonify({
            'rate_stats': [
                {
                    'work_div_nm': stat.work_div_nm,
                    'count': stat.count,
                    'avg_rate': float(stat.avg_rate) if stat.avg_rate else 0,
                    'min_rate': float(stat.min_rate) if stat.min_rate else 0,
                    'max_rate': float(stat.max_rate) if stat.max_rate else 0
                }
                for stat in rate_stats
            ]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

