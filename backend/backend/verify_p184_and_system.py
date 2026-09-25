"""
Automated Verification & P184 Evidence Suite
Construction SOI Platform - Engineers Veedu
Author: Suthanthiran P.
"""

import sys
import os
import json
import sqlite3
import time

# Ensure proper encoding
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Import Flask app
from app import app, DB_NAME

def run_tests():
    print("=" * 70)
    print("  CONSTRUCTION SOI PLATFORM - P184 AUDIT & SYSTEM VERIFICATION SUITE")
    print("=" * 70)
    
    client = app.test_client()
    passed = 0
    total = 0

    # Test 1: Health Endpoint Check
    total += 1
    print("\n[TEST 1] Core Health Endpoint Check (GET /health)...")
    res = client.get('/health')
    if res.status_code == 200:
        data = res.get_json()
        if data.get("status") == "healthy" and "Chatbot" not in data.get("message", ""):
            print(f"  PASS: Health endpoint responded 200 OK -> {data}")
            passed += 1
        else:
            print(f"  FAIL: Unexpected response content: {data}")
    else:
        print(f"  FAIL: Status code {res.status_code}")

    # Test 2: Verify AI Chatbot Decommissioning (/chat returns 404)
    total += 1
    print("\n[TEST 2] Verifying Decommissioning of /chat Endpoint...")
    res = client.post('/chat', json={"message": "hello"})
    if res.status_code == 404:
        print("  PASS: POST /chat returned 404 Not Found (Successfully removed)")
        passed += 1
    else:
        print(f"  FAIL: Expected 404 for /chat, got {res.status_code}")

    # Test 3: Verify Decommissioning of /clear and /regenerate-embeddings
    total += 1
    print("\n[TEST 3] Verifying Removal of Ancillary Chatbot Endpoints...")
    res_clear = client.post('/clear', json={})
    res_regen = client.post('/regenerate-embeddings', json={})
    if res_clear.status_code == 404 and res_regen.status_code == 404:
        print("  PASS: POST /clear and /regenerate-embeddings returned 404 Not Found")
        passed += 1
    else:
        print(f"  FAIL: Expected 404, got clear: {res_clear.status_code}, regen: {res_regen.status_code}")

    # Test 4: Database Integrity & Daily Logs Audit (P184 Item 5)
    total += 1
    print("\n[TEST 4] Database Daily Logs Completeness Audit (Item 5)...")
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM daily_logs")
        count = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) FROM daily_logs WHERE logged_by IS NOT NULL")
        attributed = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) FROM daily_logs WHERE logged_by IS NULL")
        unattributed = cursor.fetchone()[0]
        
        print(f"  Total Daily Logs in Record: {count}")
        print(f"  Fully Attributed Logs: {attributed}")
        print(f"  Security Boundary Test Logs (logged_by=NULL): {unattributed}")
        
        if count == 12 and attributed == 10 and unattributed == 2:
            print("  PASS: 12-log database audit matches exact P184 Item 5 specification.")
            passed += 1
        else:
            print(f"  FAIL: Unexpected counts: total={count}, attributed={attributed}")

    # Test 5: Deterministic Civil-Engineering Analytics Engine (P184 Item 8)
    total += 1
    print("\n[TEST 5] Deterministic Civil Analytics Evaluation (Item 8)...")
    res = client.get('/api/projects/1/analysis')
    if res.status_code == 200:
        data = res.get_json()
        ai_source = data.get("ai_source")
        insights = data.get("ai_insights", {})
        eff_rating = insights.get("efficiency_rating")
        rec_count = len(insights.get("actionable_recommendations", []))
        
        if ai_source == "deterministic_civil_engine" and rec_count >= 3:
            print(f"  PASS: Analytics generated via '{ai_source}'.")
            print(f"        Efficiency: {eff_rating}, Schedule: {data.get('schedule_status')}")
            print(f"        Actionable Recommendations Count: {rec_count}")
            passed += 1
        else:
            print(f"  FAIL: Unexpected analytics structure: {data}")
    else:
        print(f"  FAIL: Status code {res.status_code}")

    # Test 6: Timeliness & Transaction Latency (P184 Item 7)
    total += 1
    print("\n[TEST 6] Timeliness & Database Query Benchmark (Item 7)...")
    timings = []
    for _ in range(10):
        t0 = time.perf_counter()
        client.get('/projects')
        t1 = time.perf_counter()
        timings.append((t1 - t0) * 1000)
    
    avg_latency = sum(timings) / len(timings)
    print(f"  Mean Request Latency across 10 trials: {avg_latency:.2f} ms")
    if avg_latency < 50.0:
        print(f"  PASS: Request latency {avg_latency:.2f} ms is well under 300 ms SLA threshold.")
        passed += 1
    else:
        print(f"  FAIL: High latency: {avg_latency:.2f} ms")

    # Test 7: Tri-Party User Directory Verification (P184 Item 1 & 6)
    total += 1
    print("\n[TEST 7] Tri-Party Users Verification (Client, Contractor, Engineer)...")
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role, count(*) FROM users GROUP BY role")
        roles = dict(cursor.fetchall())
        print(f"  Configured user roles: {roles}")
        if 'client' in roles and 'contractor' in roles and 'site_engineer' in roles:
            print("  PASS: All 3 stakeholder roles verified in authentication store.")
            passed += 1
        else:
            print(f"  FAIL: Missing expected roles in {roles}")

    # Summary
    print("\n" + "=" * 70)
    print(f"  TEST RESULTS: {passed}/{total} Passed ({(passed/total)*100:.1f}%)")
    print("=" * 70)
    return passed == total

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
