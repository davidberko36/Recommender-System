#!/usr/bin/env python3
"""
Integration Test Suite for E-commerce Recommender System
Tests both frontend and backend connectivity
"""

import requests
import json
import time

def test_backend_api():
    """Test all backend API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Backend API Endpoints...")
    print("=" * 50)
    
    tests = [
        {
            'name': 'Health Check',
            'url': f'{base_url}/api/health',
            'expected_keys': ['status', 'message']
        },
        {
            'name': 'Get Products',
            'url': f'{base_url}/api/products',
            'expected_keys': ['products', 'total']
        },
        {
            'name': 'Get Recommendations',
            'url': f'{base_url}/api/recommendations',
            'expected_keys': ['recommendations']
        },
        {
            'name': 'Get Categories',
            'url': f'{base_url}/api/categories',
            'expected_keys': ['categories']
        }
    ]
    
    results = []
    
    for test in tests:
        try:
            print(f"Testing: {test['name']}...")
            response = requests.get(test['url'], timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if expected keys are present
                has_expected_keys = all(key in data for key in test['expected_keys'])
                
                if has_expected_keys:
                    print(f"✅ {test['name']}: PASSED")
                    results.append({'test': test['name'], 'status': 'PASSED', 'data': data})
                else:
                    print(f"⚠️ {test['name']}: PARTIAL - Missing expected keys")
                    results.append({'test': test['name'], 'status': 'PARTIAL', 'data': data})
            else:
                print(f"❌ {test['name']}: FAILED (Status: {response.status_code})")
                results.append({'test': test['name'], 'status': 'FAILED', 'error': f"HTTP {response.status_code}"})
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {test['name']}: FAILED (Connection Error)")
            results.append({'test': test['name'], 'status': 'FAILED', 'error': 'Connection Error'})
        except Exception as e:
            print(f"❌ {test['name']}: FAILED ({str(e)})")
            results.append({'test': test['name'], 'status': 'FAILED', 'error': str(e)})
    
    return results

def test_frontend_connectivity():
    """Test if frontend is accessible"""
    print("\n🌐 Testing Frontend Connectivity...")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend: ACCESSIBLE")
            return True
        else:
            print(f"❌ Frontend: FAILED (Status: {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Frontend: NOT ACCESSIBLE (Connection Error)")
        return False
    except Exception as e:
        print(f"❌ Frontend: FAILED ({str(e)})")
        return False

def test_integration():
    """Test frontend-backend integration"""
    print("\n🔗 Testing Frontend-Backend Integration...")
    print("=" * 50)
    
    # Test if frontend can make requests to backend
    # This would require checking browser network requests
    # For now, we'll just check if both are running
    
    frontend_ok = test_frontend_connectivity()
    backend_results = test_backend_api()
    
    backend_ok = all(result['status'] == 'PASSED' for result in backend_results)
    
    if frontend_ok and backend_ok:
        print("✅ Integration: Both frontend and backend are running properly")
        return True
    else:
        print("❌ Integration: Issues detected")
        return False

def print_summary(backend_results, frontend_ok, integration_ok):
    """Print test summary"""
    print("\n📊 TEST SUMMARY")
    print("=" * 50)
    
    # Backend summary
    passed = sum(1 for r in backend_results if r['status'] == 'PASSED')
    total = len(backend_results)
    print(f"Backend API Tests: {passed}/{total} passed")
    
    # Frontend summary
    print(f"Frontend Accessibility: {'✅ PASS' if frontend_ok else '❌ FAIL'}")
    
    # Integration summary
    print(f"Integration Status: {'✅ PASS' if integration_ok else '❌ FAIL'}")
    
    # Overall status
    overall_ok = frontend_ok and integration_ok and passed == total
    print(f"\nOverall Status: {'🎉 ALL SYSTEMS GO!' if overall_ok else '⚠️ ISSUES DETECTED'}")
    
    if overall_ok:
        print("\n🚀 Your E-commerce Recommender System is fully operational!")
        print("📱 Frontend: http://localhost:3000")
        print("🔗 Backend API: http://localhost:5000")
        print("🤖 Recommender: Ready for AI recommendations")
        print("🇧🇷 Dataset: Brazilian E-commerce (Olist) data loaded")

def main():
    """Main test function"""
    print("🧪 E-COMMERCE RECOMMENDER SYSTEM - INTEGRATION TESTS")
    print("=" * 60)
    
    # Test backend
    backend_results = test_backend_api()
    
    # Test frontend
    frontend_ok = test_frontend_connectivity()
    
    # Test integration
    integration_ok = test_integration()
    
    # Print summary
    print_summary(backend_results, frontend_ok, integration_ok)
    
    # Sample data preview
    print("\n📝 Sample API Data:")
    print("-" * 30)
    
    try:
        response = requests.get("http://localhost:5000/api/products?per_page=3")
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])
            for i, product in enumerate(products[:3], 1):
                print(f"{i}. {product.get('name', 'Unknown')} - ${product.get('price', 0)}")
        else:
            print("Could not fetch sample data")
    except:
        print("Could not fetch sample data")

if __name__ == "__main__":
    main()
