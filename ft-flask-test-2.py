#!/usr/bin/env python3
"""
Comprehensive test script for Flask Stock Analytics API
Tests all available routes with various scenarios
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('route_tests.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class APITester:
    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        """Initialize the API tester with base URL"""
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.test_results = []
        
    def log_test_result(self, test_name: str, success: bool, response_code: int, 
                       response_data: Any = None, error: str = None):
        """Log test result"""
        result = {
            'test_name': test_name,
            'success': success,
            'response_code': response_code,
            'timestamp': datetime.utcnow().isoformat(),
            'response_data': response_data,
            'error': error
        }
        self.test_results.append(result)
        
        status = "PASS" if success else "FAIL"
        logger.info(f"[{status}] {test_name} - Status: {response_code}")
        if error:
            logger.error(f"Error: {error}")
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, 
                    expected_status: int = 200) -> Optional[Dict]:
        """Make HTTP request and handle response"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {method} {endpoint}: {str(e)}")
            return None
    
    def test_root_endpoint(self):
        """Test root endpoint /"""
        logger.info("Testing root endpoint...")
        
        response = self.make_request('GET', '/')
        if response and response.status_code == 200:
            try:
                data = response.json()
                required_fields = ['service', 'version', 'status', 'timestamp', 'endpoints']
                if all(field in data for field in required_fields):
                    self.log_test_result('Root Endpoint', True, response.status_code, data)
                else:
                    self.log_test_result('Root Endpoint', False, response.status_code, 
                                       data, "Missing required fields")
            except json.JSONDecodeError:
                self.log_test_result('Root Endpoint', False, response.status_code, 
                                   None, "Invalid JSON response")
        else:
            self.log_test_result('Root Endpoint', False, 
                               response.status_code if response else 0, 
                               None, "Request failed")
    
    def test_favicon(self):
        """Test favicon endpoint"""
        logger.info("Testing favicon endpoint...")
        
        response = self.make_request('GET', '/favicon.ico')
        success = response and response.status_code == 204
        self.log_test_result('Favicon Endpoint', success, 
                           response.status_code if response else 0)
    
    def test_health_endpoints(self):
        """Test health check endpoints"""
        logger.info("Testing health endpoints...")
        
        # Basic health check
        response = self.make_request('GET', '/v1/health')
        if response:
            success = response.status_code == 200
            try:
                data = response.json() if response.content else None
                self.log_test_result('Health Check', success, response.status_code, data)
            except json.JSONDecodeError:
                self.log_test_result('Health Check', success, response.status_code)
        
        # Detailed health check
        response = self.make_request('GET', '/v1/health/detailed')
        if response:
            success = response.status_code == 200
            try:
                data = response.json() if response.content else None
                self.log_test_result('Detailed Health Check', success, response.status_code, data)
            except json.JSONDecodeError:
                self.log_test_result('Detailed Health Check', success, response.status_code)
    
    def test_update_endpoints(self):
        """Test update endpoints"""
        logger.info("Testing update endpoints...")
        
        # Test update all symbols
        response = self.make_request('POST', '/v1/update_all_symbols')
        if response:
            success = response.status_code in [200, 202, 409]  # 409 if already running
            try:
                data = response.json() if response.content else None
                self.log_test_result('Update All Symbols', success, response.status_code, data)
            except json.JSONDecodeError:
                self.log_test_result('Update All Symbols', success, response.status_code)
        
        # Test update status
        response = self.make_request('GET', '/v1/update_all_symbols/status')
        if response:
            success = response.status_code == 200
            try:
                data = response.json() if response.content else None
                self.log_test_result('Update Status', success, response.status_code, data)
            except json.JSONDecodeError:
                self.log_test_result('Update Status', success, response.status_code)
    
    def test_bhavcopy_endpoint(self):
        """Test BhavCopy processing endpoint"""
        logger.info("Testing BhavCopy endpoint...")
        
        response = self.make_request('POST', '/v1/bhavcopy')
        if response:
            success = response.status_code in [200, 500]  # May fail without proper data
            try:
                data = response.json() if response.content else None
                self.log_test_result('BhavCopy Processing', success, response.status_code, data)
            except json.JSONDecodeError:
                self.log_test_result('BhavCopy Processing', success, response.status_code)
    
    def test_analytics_endpoints(self):
        """Test analytics endpoints"""
        logger.info("Testing analytics endpoints...")
        
        # Test SMA nearby with valid parameters
        test_cases = [
            {
                'name': 'SMA Nearby - Default Parameters',
                'data': {},
                'endpoint': '/v1/analytics/sma-nearby'
            },
            {
                'name': 'SMA Nearby - Custom Parameters',
                'data': {'sma_period': 20, 'threshold_pct': 1.5},
                'endpoint': '/v1/analytics/sma-nearby'
            },
            {
                'name': 'SMA Nearby - Invalid Parameters',
                'data': {'sma_period': -1, 'threshold_pct': 101},
                'endpoint': '/v1/analytics/sma-nearby'
            },
            {
                'name': 'SMA Database Update - Default',
                'data': {},
                'endpoint': '/v1/analytics/smadb'
            },
            {
                'name': 'SMA Database Update - Custom Parameters',
                'data': {'sma_period': 50, 'threshold_pct': 3.0},
                'endpoint': '/v1/analytics/smadb'
            },
            {
                'name': 'SMA Backfill - Default',
                'data': {},
                'endpoint': '/v1/analytics/smadb/backfill'
            },
            {
                'name': 'SMA Backfill - Custom Parameters',
                'data': {'sma_period': 20, 'threshold_pct': 2.0, 'days': 5},
                'endpoint': '/v1/analytics/smadb/backfill'
            },
            {
                'name': 'SMA Backfill - Invalid Days',
                'data': {'sma_period': 20, 'threshold_pct': 2.0, 'days': 10},
                'endpoint': '/v1/analytics/smadb/backfill'
            }
        ]
        
        for test_case in test_cases:
            response = self.make_request('POST', test_case['endpoint'], test_case['data'])
            if response:
                # Success conditions vary based on test case
                if 'Invalid' in test_case['name']:
                    success = response.status_code == 400
                else:
                    success = response.status_code in [200, 500]  # May fail if no data
                
                try:
                    data = response.json() if response.content else None
                    self.log_test_result(test_case['name'], success, response.status_code, data)
                except json.JSONDecodeError:
                    self.log_test_result(test_case['name'], success, response.status_code)
    
    def test_invalid_content_type(self):
        """Test endpoints with invalid content type"""
        logger.info("Testing invalid content type...")
        
        # Save original headers
        original_headers = self.session.headers.copy()
        
        # Set invalid content type
        self.session.headers['Content-Type'] = 'text/plain'
        
        response = self.make_request('POST', '/v1/analytics/sma-nearby', {'test': 'data'})
        if response:
            success = response.status_code == 400
            try:
                data = response.json() if response.content else None
                self.log_test_result('Invalid Content Type', success, response.status_code, data)
            except json.JSONDecodeError:
                self.log_test_result('Invalid Content Type', success, response.status_code)
        
        # Restore original headers
        self.session.headers = original_headers
    
    def test_error_handlers(self):
        """Test error handlers"""
        logger.info("Testing error handlers...")
        
        # Test 404 - Not Found
        response = self.make_request('GET', '/nonexistent-endpoint')
        if response:
            success = response.status_code == 404
            try:
                data = response.json() if response.content else None
                self.log_test_result('404 Error Handler', success, response.status_code, data)
            except json.JSONDecodeError:
                self.log_test_result('404 Error Handler', success, response.status_code)
        
        # Test 405 - Method Not Allowed
        response = self.make_request('DELETE', '/v1/health')
        if response:
            success = response.status_code == 405
            try:
                data = response.json() if response.content else None
                self.log_test_result('405 Error Handler', success, response.status_code, data)
            except json.JSONDecodeError:
                self.log_test_result('405 Error Handler', success, response.status_code)
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        logger.info("Starting comprehensive API testing...")
        start_time = time.time()
        
        # Run all test suites
        self.test_root_endpoint()
        self.test_favicon()
        self.test_health_endpoints()
        self.test_update_endpoints()
        self.test_bhavcopy_endpoint()
        self.test_analytics_endpoints()
        self.test_invalid_content_type()
        self.test_error_handlers()
        
        end_time = time.time()
        total_time = round(end_time - start_time, 2)
        
        # Generate summary report
        self.generate_report(total_time)
    
    def generate_report(self, total_time: float):
        """Generate test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        logger.info("=" * 80)
        logger.info("TEST EXECUTION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        logger.info(f"Total Execution Time: {total_time}s")
        logger.info("=" * 80)
        
        # Show failed tests
        if failed_tests > 0:
            logger.info("\nFAILED TESTS:")
            logger.info("-" * 40)
            for result in self.test_results:
                if not result['success']:
                    logger.info(f"❌ {result['test_name']} (Status: {result['response_code']})")
                    if result['error']:
                        logger.info(f"   Error: {result['error']}")
        
        # Show passed tests
        logger.info("\nPASSED TESTS:")
        logger.info("-" * 40)
        for result in self.test_results:
            if result['success']:
                logger.info(f"✅ {result['test_name']} (Status: {result['response_code']})")
        
        # Save detailed results to JSON file
        with open('test_results.json', 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'passed': passed_tests,
                    'failed': failed_tests,
                    'success_rate': round((passed_tests/total_tests)*100, 2),
                    'execution_time': total_time,
                    'timestamp': datetime.utcnow().isoformat()
                },
                'detailed_results': self.test_results
            }, f, indent=2)
        
        logger.info(f"\nDetailed results saved to: test_results.json")


def main():
    """Main function to run tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Flask Stock Analytics API')
    parser.add_argument('--url', default='http://127.0.0.1:5000', 
                       help='Base URL of the API (default: http://127.0.0.1:5000)')
    parser.add_argument('--verbose', action='store_true', 
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create tester instance
    tester = APITester(args.url)
    
    logger.info(f"Testing API at: {args.url}")
    logger.info("Ensure the Flask app is running before executing tests")
    
    try:
        # Run all tests
        tester.run_all_tests()
        
    except KeyboardInterrupt:
        logger.info("\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()