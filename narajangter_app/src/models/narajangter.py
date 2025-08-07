from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class BidNotice(db.Model):
    """입찰공고 정보 모델"""
    __tablename__ = 'bid_notices'
    
    id = db.Column(db.Integer, primary_key=True)
    bid_notice_no = db.Column(db.String(50), unique=True, nullable=False)  # 입찰공고번호
    bid_notice_nm = db.Column(db.String(500), nullable=False)  # 입찰공고명
    bid_notice_ord = db.Column(db.String(10))  # 입찰공고차수
    dminstt_nm = db.Column(db.String(200))  # 수요기관명
    rgst_dt = db.Column(db.DateTime)  # 등록일시
    bid_begin_dt = db.Column(db.DateTime)  # 입찰개시일시
    bid_close_dt = db.Column(db.DateTime)  # 입찰마감일시
    openg_dt = db.Column(db.DateTime)  # 개찰일시
    presmpt_price = db.Column(db.BigInteger)  # 추정가격
    basic_amount = db.Column(db.BigInteger)  # 기초금액
    bid_method_nm = db.Column(db.String(100))  # 입찰방식명
    cntrct_cncls_mthd_nm = db.Column(db.String(100))  # 계약체결방법명
    work_div_nm = db.Column(db.String(50))  # 업무구분명
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'bid_notice_no': self.bid_notice_no,
            'bid_notice_nm': self.bid_notice_nm,
            'bid_notice_ord': self.bid_notice_ord,
            'dminstt_nm': self.dminstt_nm,
            'rgst_dt': self.rgst_dt.isoformat() if self.rgst_dt else None,
            'bid_begin_dt': self.bid_begin_dt.isoformat() if self.bid_begin_dt else None,
            'bid_close_dt': self.bid_close_dt.isoformat() if self.bid_close_dt else None,
            'openg_dt': self.openg_dt.isoformat() if self.openg_dt else None,
            'presmpt_price': self.presmpt_price,
            'basic_amount': self.basic_amount,
            'bid_method_nm': self.bid_method_nm,
            'cntrct_cncls_mthd_nm': self.cntrct_cncls_mthd_nm,
            'work_div_nm': self.work_div_nm,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SuccessfulBid(db.Model):
    """낙찰 정보 모델"""
    __tablename__ = 'successful_bids'
    
    id = db.Column(db.Integer, primary_key=True)
    bid_notice_no = db.Column(db.String(50), nullable=False)  # 입찰공고번호
    bid_notice_ord = db.Column(db.String(10))  # 입찰공고차수
    openg_dt = db.Column(db.DateTime)  # 개찰일시
    scsbid_corp_nm = db.Column(db.String(200))  # 낙찰업체명
    scsbid_amount = db.Column(db.BigInteger)  # 낙찰금액
    presmpt_price = db.Column(db.BigInteger)  # 추정가격
    scsbid_rate = db.Column(db.Float)  # 낙찰률
    work_div_nm = db.Column(db.String(50))  # 업무구분명
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'bid_notice_no': self.bid_notice_no,
            'bid_notice_ord': self.bid_notice_ord,
            'openg_dt': self.openg_dt.isoformat() if self.openg_dt else None,
            'scsbid_corp_nm': self.scsbid_corp_nm,
            'scsbid_amount': self.scsbid_amount,
            'presmpt_price': self.presmpt_price,
            'scsbid_rate': self.scsbid_rate,
            'work_div_nm': self.work_div_nm,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ApiConfig(db.Model):
    """API 설정 정보 모델"""
    __tablename__ = 'api_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    service_key = db.Column(db.String(500), nullable=False)  # 공공데이터포털 서비스키
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'service_key': self.service_key[:10] + '...' if self.service_key else None,  # 보안상 일부만 표시
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

