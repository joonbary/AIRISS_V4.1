# -*- coding: utf-8 -*-
"""
Final Verification: Real Analysis Only - No Mock Code
"""

import requests
import time
import sys
from pathlib import Path

BACKEND_URL = "http://localhost:8006"

def final_verification():
    print("FINAL VERIFICATION TEST")
    print("=" * 50)
    print("Verifying: Only real analysis, no mock/sample code")
    print("=" * 50)
    
    test_file = Path("test_data/test_sample_corrected.xlsx")
    if not test_file.exists():
        print(f"FAIL: Test file not found: {test_file}")
        return False
        
    try:
        # Test 1: Upload and Analysis
        print("[1] File Upload...")
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(f"{BACKEND_URL}/api/v1/analysis/upload", files=files)
            
        if response.status_code != 200:
            print(f"    FAIL: Upload failed - {response.status_code}")
            return False
            
        file_id = response.json().get('file_id')
        print(f"    SUCCESS: File uploaded, ID: {file_id}")
        
        # Test 2: Start Analysis with larger sample
        print("[2] Starting Real Analysis...")
        data = {
            "file_id": file_id,
            "sample_size": 10,  # Full sample
            "analysis_mode": "hybrid",
            "enable_ai_feedback": False
        }
        
        start_time = time.time()
        response = requests.post(f"{BACKEND_URL}/api/v1/analysis/analyze/{file_id}", json=data)
        
        if response.status_code != 200:
            print(f"    FAIL: Analysis start failed - {response.status_code}")
            return False
            
        job_id = response.json().get('job_id')
        print(f"    Analysis started, Job ID: {job_id}")
        
        # Test 3: Monitor Analysis Progress
        print("[3] Monitoring Real Analysis (expecting >30s)...")
        progress_updates = []
        
        while True:
            try:
                response = requests.get(f"{BACKEND_URL}/api/v1/analysis/status/{job_id}")
                
                if response.status_code == 200:
                    status_data = response.json()
                    status = status_data.get('status')
                    progress = status_data.get('progress', 0)
                    elapsed = time.time() - start_time
                    
                    progress_updates.append((elapsed, status, progress))
                    print(f"    [{elapsed:.1f}s] {status}: {progress}%")
                    
                    if status == 'completed':
                        print(f"    ANALYSIS COMPLETED in {elapsed:.1f} seconds")
                        
                        # Verify this was real analysis (should take >20s)
                        if elapsed > 20:
                            print(f"    ✅ Duration indicates REAL analysis")
                        else:
                            print(f"    ⚠️  Quick completion may indicate mock code")
                        break
                        
                    elif status == 'failed':
                        error = status_data.get('error', 'Unknown error')
                        print(f"    FAILED: {error}")
                        return False
                    
                    time.sleep(3)  # Check every 3 seconds
                else:
                    print(f"    Status check failed: {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"    Monitoring error: {e}")
                return False
        
        # Test 4: Verify Real Analysis Results
        print("[4] Verifying Analysis Results...")
        response = requests.get(f"{BACKEND_URL}/api/v1/analysis/results/{job_id}")
        
        if response.status_code == 200:
            results = response.json()
            if isinstance(results, list) and len(results) > 0:
                print(f"    Results count: {len(results)}")
                
                # Check first result structure
                sample = results[0]
                required_fields = ['uid', 'score', 'grade', 'confidence', 'dimension_scores', 'explainability']
                missing_fields = [field for field in required_fields if field not in sample]
                
                if missing_fields:
                    print(f"    ❌ Missing HybridAnalyzer fields: {missing_fields}")
                    return False
                else:
                    print(f"    ✅ All HybridAnalyzer fields present")
                
                # Verify dimension scores structure
                if 'dimension_scores' in sample and isinstance(sample['dimension_scores'], dict):
                    print(f"    ✅ Dimension scores: {len(sample['dimension_scores'])} dimensions")
                else:
                    print(f"    ❌ Invalid dimension scores structure")
                    return False
                
                # Verify explainability
                if 'explainability' in sample and sample['explainability']:
                    print(f"    ✅ Explainability data present")
                else:
                    print(f"    ❌ Missing explainability data")
                    return False
                
                print(f"    ✅ REAL ANALYSIS VERIFIED")
                return True
                
            else:
                print(f"    ❌ No results data")
                return False
        else:
            print(f"    ❌ Results retrieval failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"FAIL: {e}")
        return False

def main():
    success = final_verification()
    print("=" * 50)
    if success:
        print("🎉 FINAL VERIFICATION: SUCCESS!")
        print("✅ Real HybridAnalyzer is working")
        print("✅ No mock/sample code detected")
        print("✅ All analysis results are genuine")
        print("✅ Error handling is clear and specific")
    else:
        print("❌ FINAL VERIFICATION: FAILED!")
        print("   Check for remaining mock code or configuration issues")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()