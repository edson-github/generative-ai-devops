#!/usr/bin/env python3
import requests
import sys
from time import sleep
from typing import Dict, List

def check_service(url: str, service_name: str, expected_status: int = 200, retries: int = 3) -> Dict:
    """Check if a service is responding correctly."""
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=5)
            return {
                "service": service_name,
                "url": url,
                "status": response.status_code,
                "success": response.status_code == expected_status,
                "error": None
            }
        except requests.RequestException as e:
            if attempt == retries - 1:
                return {
                    "service": service_name,
                    "url": url,
                    "status": None,
                    "success": False,
                    "error": str(e)
                }
            sleep(2)  # Wait before retry

def run_smoke_tests() -> List[Dict]:
    """Run smoke tests for all services."""
    services = [
        {"name": "Backend API", "url": "http://localhost:8000/docs", "expected_status": 200},
        {"name": "Frontend", "url": "http://localhost:8501", "expected_status": 200},
        {"name": "Prometheus", "url": "http://localhost:9090", "expected_status": 200},
    ]
    
    results = []
    for service in services:
        result = check_service(
            service["url"], 
            service["name"], 
            service["expected_status"]
        )
        results.append(result)
    return results

def print_results(results: List[Dict]) -> None:
    """Print test results in a formatted way."""
    print("\n=== Smoke Tests Results ===")
    all_success = True
    
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"\n{status} - {result['service']}")
        print(f"URL: {result['url']}")
        
        if result["status"]:
            print(f"Status Code: {result['status']}")
        if result["error"]:
            print(f"Error: {result['error']}")
            
        all_success = all_success and result["success"]
    
    print("\n=== Summary ===")
    print(f"Total Services: {len(results)}")
    print(f"Successful: {sum(1 for r in results if r['success'])}")
    print(f"Failed: {sum(1 for r in results if not r['success'])}")
    
    sys.exit(0 if all_success else 1)

if __name__ == "__main__":
    results = run_smoke_tests()
    print_results(results)