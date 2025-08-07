import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../narajangter_app/src'))

from utils.api_helper import NarajangterAPI

class TestNarajangterAPI(unittest.TestCase):
    def setUp(self):
        self.api = NarajangterAPI("test_service_key")
    
    @patch('utils.api_helper.requests.get')
    def test_get_bid_notices_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'response': {
                'body': {
                    'items': [
                        {
                            'bidNtceNo': '20250001234',
                            'bidNtceNm': 'Test Bid Notice',
                            'dminsttNm': 'Test Organization'
                        }
                    ],
                    'totalCount': 1
                }
            }
        }
        mock_get.return_value = mock_response
        
        result = self.api.get_bid_notices('20250101', '20250131')
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result['items']), 1)
        self.assertEqual(result['totalCount'], 1)
    
    @patch('utils.api_helper.requests.get')
    def test_get_bid_notices_api_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        result = self.api.get_bid_notices('20250101', '20250131')
        
        self.assertIsNone(result)
    
    @patch('utils.api_helper.requests.get')
    def test_get_successful_bids_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'response': {
                'body': {
                    'items': [
                        {
                            'bidNtceNo': '20250001234',
                            'scsbidCorpNm': 'Test Company',
                            'scsbidAmount': 1000000
                        }
                    ],
                    'totalCount': 1
                }
            }
        }
        mock_get.return_value = mock_response
        
        result = self.api.get_successful_bids('20250101', '20250107')
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result['items']), 1)
        self.assertEqual(result['totalCount'], 1)

if __name__ == '__main__':
    unittest.main()