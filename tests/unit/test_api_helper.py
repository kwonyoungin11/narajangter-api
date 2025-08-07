import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../narajangter_app/src'))

from utils.api_helper import APIHelper

class TestAPIHelper(unittest.TestCase):
    def setUp(self):
        self.api_helper = APIHelper()
    
    @patch('utils.api_helper.requests.get')
    def test_call_api_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'test content'
        mock_get.return_value = mock_response
        
        result = self.api_helper.call_api('http://test.com', {'param': 'value'})
        
        self.assertIsNotNone(result)
        self.assertEqual(result.status_code, 200)
    
    @patch('utils.api_helper.requests.get')
    def test_call_api_server_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        result = self.api_helper.call_api('http://test.com', {'param': 'value'}, retry=False)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.status_code, 500)
    
    def test_parse_api_response_success(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'response': {
                'header': {
                    'resultCode': '00',
                    'resultMsg': 'SUCCESS'
                },
                'body': {
                    'items': [
                        {
                            'bidNtceNo': '20250001234',
                            'bidNtceNm': 'Test Bid Notice'
                        }
                    ],
                    'totalCount': 1
                }
            }
        }
        
        result = self.api_helper.parse_api_response(mock_response)
        
        self.assertTrue(result['success'])
        self.assertEqual(len(result['items']), 1)
        self.assertEqual(result['total_count'], 1)
    
    def test_validate_date_range(self):
        # Valid range
        self.assertTrue(self.api_helper.validate_date_range('20250101', '20250131'))
        
        # Invalid range (too long)
        self.assertFalse(self.api_helper.validate_date_range('20250101', '20250301'))
        
        # Invalid range (end before start)
        self.assertFalse(self.api_helper.validate_date_range('20250131', '20250101'))

if __name__ == '__main__':
    unittest.main()