#!/usr/bin/env python3
"""
Backend API Testing for The Ember Scriptorium v1
Tests all API endpoints and functionality
"""

import requests
import json
import sys
import csv
from datetime import datetime
import base64

class EmberScriptoriumTester:
    def __init__(self, base_url="https://6fdc1bd5-6f98-4b4f-9645-e88780e02f59.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.sample_quotes = []
        
    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        if details and success:
            print(f"   Details: {details}")
        print()

    def test_root_endpoint(self):
        """Test the root endpoint (frontend serves HTML, so we test API connectivity)"""
        try:
            # Test API connectivity instead of root HTML
            response = requests.get(f"{self.base_url}/api/quotes", timeout=10)
            success = response.status_code == 200
            details = f"API Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", API responding correctly"
            self.log_test("API Connectivity", success, details)
            return success
        except Exception as e:
            self.log_test("API Connectivity", False, str(e))
            return False

    def load_sample_quotes(self):
        """Load sample quotes from CSV"""
        try:
            with open('/app/sample_quotes.csv', 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self.sample_quotes = list(reader)
            
            success = len(self.sample_quotes) > 0
            details = f"Loaded {len(self.sample_quotes)} quotes"
            self.log_test("Load Sample Quotes", success, details)
            return success
        except Exception as e:
            self.log_test("Load Sample Quotes", False, str(e))
            return False

    def test_upload_quotes(self):
        """Test quote upload endpoint"""
        if not self.sample_quotes:
            self.log_test("Upload Quotes", False, "No sample quotes loaded")
            return False
            
        try:
            # Prepare quotes data
            quotes_data = []
            for quote in self.sample_quotes[:5]:  # Upload first 5 quotes for testing
                quotes_data.append({
                    "quote": quote.get("quote", "").strip('"'),
                    "theme": quote.get("theme", ""),
                    "tone": quote.get("tone", ""),
                    "length": quote.get("length", ""),
                    "visual_keywords": quote.get("visual_keywords", "")
                })
            
            payload = {"quotes": quotes_data}
            response = requests.post(
                f"{self.base_url}/api/quotes/upload",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
            else:
                try:
                    error_data = response.json()
                    details += f", Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details += f", Response: {response.text[:200]}"
                    
            self.log_test("Upload Quotes", success, details)
            return success
        except Exception as e:
            self.log_test("Upload Quotes", False, str(e))
            return False

    def test_get_quotes(self):
        """Test get quotes endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/quotes", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                quotes_count = len(data.get('quotes', []))
                total = data.get('total', 0)
                details += f", Retrieved: {quotes_count} quotes, Total: {total}"
            else:
                try:
                    error_data = response.json()
                    details += f", Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details += f", Response: {response.text[:200]}"
                    
            self.log_test("Get Quotes", success, details)
            return success
        except Exception as e:
            self.log_test("Get Quotes", False, str(e))
            return False

    def test_get_settings(self):
        """Test get settings endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/settings", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                configured = data.get('configured', False)
                has_openai = data.get('has_openai_key', False)
                details += f", Configured: {configured}, Has OpenAI Key: {has_openai}"
            else:
                try:
                    error_data = response.json()
                    details += f", Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details += f", Response: {response.text[:200]}"
                    
            self.log_test("Get Settings", success, details)
            return success
        except Exception as e:
            self.log_test("Get Settings", False, str(e))
            return False

    def test_update_settings(self):
        """Test update settings endpoint (without real API key)"""
        try:
            # Test with dummy data to check endpoint functionality
            payload = {
                "openai_api_key": "test-key-for-endpoint-testing"
            }
            response = requests.post(
                f"{self.base_url}/api/settings",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
            else:
                try:
                    error_data = response.json()
                    details += f", Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details += f", Response: {response.text[:200]}"
                    
            self.log_test("Update Settings", success, details)
            return success
        except Exception as e:
            self.log_test("Update Settings", False, str(e))
            return False

    def test_get_posts_queue(self):
        """Test get posts queue endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/posts/queue", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                posts_count = len(data.get('posts', []))
                details += f", Queue posts: {posts_count}"
            else:
                try:
                    error_data = response.json()
                    details += f", Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details += f", Response: {response.text[:200]}"
                    
            self.log_test("Get Posts Queue", success, details)
            return success
        except Exception as e:
            self.log_test("Get Posts Queue", False, str(e))
            return False

    def test_get_approved_posts(self):
        """Test get approved posts endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/posts/approved", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                posts_count = len(data.get('posts', []))
                details += f", Approved posts: {posts_count}"
            else:
                try:
                    error_data = response.json()
                    details += f", Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details += f", Response: {response.text[:200]}"
                    
            self.log_test("Get Approved Posts", success, details)
            return success
        except Exception as e:
            self.log_test("Get Approved Posts", False, str(e))
            return False

    def test_generate_post(self):
        """Test post generation endpoint (expected to fail without OpenAI key)"""
        try:
            response = requests.post(f"{self.base_url}/api/posts/generate", timeout=15)
            
            # We expect this to fail without OpenAI API key
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    if "OpenAI API key not configured" in error_data.get('detail', ''):
                        success = True
                        details = "Expected failure - OpenAI API key not configured"
                    else:
                        success = False
                        details = f"Unexpected error: {error_data.get('detail', 'Unknown error')}"
                except:
                    success = False
                    details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            elif response.status_code == 200:
                success = True
                details = "Post generated successfully (OpenAI key configured)"
            else:
                success = False
                details = f"Status: {response.status_code}"
                try:
                    error_data = response.json()
                    details += f", Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details += f", Response: {response.text[:200]}"
                    
            self.log_test("Generate Post", success, details)
            return success
        except Exception as e:
            self.log_test("Generate Post", False, str(e))
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print("🔥 The Ember Scriptorium v1 - Backend API Testing")
        print("=" * 60)
        print()
        
        # Test basic connectivity
        if not self.test_root_endpoint():
            print("❌ API connectivity failed - stopping tests")
            return False
            
        # Load sample data
        self.load_sample_quotes()
        
        # Test all endpoints
        self.test_upload_quotes()
        self.test_get_quotes()
        self.test_get_settings()
        self.test_update_settings()
        self.test_get_posts_queue()
        self.test_get_approved_posts()
        self.test_generate_post()
        
        # Print summary
        print("=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    """Main test runner"""
    tester = EmberScriptoriumTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())