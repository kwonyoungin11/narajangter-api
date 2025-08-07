import unittest
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../narajangter_app/src'))

from models.narajangter import BidNotice, SuccessfulBid, ApiConfig

class TestModels(unittest.TestCase):
    
    def test_bid_notice_creation(self):
        bid_notice = BidNotice(
            bid_notice_no='20250001234',
            bid_notice_nm='Test Bid Notice',
            dminstt_nm='Test Organization',
            presmpt_price=1000000,
            rgst_dt=datetime.now()
        )
        
        self.assertEqual(bid_notice.bid_notice_no, '20250001234')
        self.assertEqual(bid_notice.bid_notice_nm, 'Test Bid Notice')
        self.assertEqual(bid_notice.dminstt_nm, 'Test Organization')
        self.assertEqual(bid_notice.presmpt_price, 1000000)
    
    def test_successful_bid_creation(self):
        successful_bid = SuccessfulBid(
            bid_notice_no='20250001234',
            scsbid_corp_nm='Test Company',
            scsbid_amount=900000,
            scsbid_rate=90.0
        )
        
        self.assertEqual(successful_bid.bid_notice_no, '20250001234')
        self.assertEqual(successful_bid.scsbid_corp_nm, 'Test Company')
        self.assertEqual(successful_bid.scsbid_amount, 900000)
        self.assertEqual(successful_bid.scsbid_rate, 90.0)
    
    def test_api_config_creation(self):
        api_config = ApiConfig(
            service_key='test_key_123',
            is_active=True
        )
        
        self.assertEqual(api_config.service_key, 'test_key_123')
        self.assertTrue(api_config.is_active)

if __name__ == '__main__':
    unittest.main()