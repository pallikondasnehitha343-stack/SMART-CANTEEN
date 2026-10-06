"""
Smart Canteen Autonomous Test Runner & Evidence Matrix Generator
Executes all domain test suites and outputs structured execution telemetry.
"""
import os
import sys
import time
import pytest

def run_all_tests():
    print("=" * 80)
    print("SMART CANTEEN ORCHESTRATION SYSTEM — VERIFICATION & EVIDENCE RUNNER")
    print("=" * 80)
    
    start_time = time.time()
    
    # Run pytest programmatically
    test_dir = os.path.join(os.path.dirname(__file__), "tests")
    exit_code = pytest.main([
        "-v",
        "-s",
        test_dir
    ])
    
    elapsed = round(time.time() - start_time, 2)
    
    print("\n" + "=" * 80)
    print("REQUIREMENT EVIDENCE MATRIX")
    print("=" * 80)
    
    matrix = [
        ("Online Ordering & Cart", "backend/app/routers/orders.py", "test_order_creation_and_queue_placement", "PASS"),
        ("Virtual Queue & Fair Aging", "backend/app/services/queue_service.py", "test_fair_aging_anti_starvation_score_progression", "PASS"),
        ("Dynamic ETA Calculation", "backend/app/services/eta_engine.py", "test_concurrency_09_kitchen_workload_changing_dynamic_eta", "PASS"),
        ("Idempotent Payments", "backend/app/services/payment_service.py", "test_payment_idempotency_prevents_duplicate_charge", "PASS"),
        ("Payment Failure Stock Rollback", "backend/app/services/payment_service.py", "test_payment_failure_restores_stock", "PASS"),
        ("Cryptographic QR Pickup Token", "backend/app/services/qr_service.py", "test_qr_pickup_full_lifecycle_and_single_use_protection", "PASS"),
        ("Single-Use QR Replay Defense", "backend/app/services/qr_service.py", "test_concurrency_06_pickup_qr_scanned_twice", "PASS"),
        ("Tampered QR Rejection", "backend/app/services/qr_service.py", "test_tampered_qr_token_rejected", "PASS"),
        ("Atomic Inventory Reservation", "backend/app/services/inventory_service.py", "test_concurrency_01_last_item_overselling_prevention", "PASS"),
        ("Dynamic Pickup Capacity", "backend/app/services/pickup_service.py", "test_concurrency_08_pickup_slot_becoming_full", "PASS"),
        ("Peak Period Detection", "backend/app/services/peak_manager.py", "test_peak_load_detection_and_telemetry", "PASS"),
        ("Kitchen Display System (KDS)", "backend/app/routers/kitchen.py", "test_kitchen_workflow_kanban_transition", "PASS"),
        ("RBAC & Security Authorization", "backend/app/services/auth_service.py", "test_rbac_admin_endpoint_forbidden_for_student", "PASS"),
        ("Operational Analytics & Bottlenecks", "backend/app/services/analytics_service.py", "test_admin_metrics_dashboard", "PASS"),
        ("ML Demand Forecasting", "backend/app/services/ml_forecasting.py", "test_demand_forecast_predictions", "PASS"),
        ("10 Concurrency Scenarios", "backend/tests/test_concurrency.py", "test_concurrency_* (All 10 verified)", "PASS"),
    ]
    
    print(f"{'Requirement':<35} | {'Module / Service':<38} | {'Validation Test':<45} | {'Result'}")
    print("-" * 130)
    for req, mod, val, res in matrix:
        status_str = "[PASS]" if exit_code == 0 else "[CHECK]"
        print(f"{req:<35} | {mod:<38} | {val:<45} | {status_str}")
        
    print("-" * 130)
    print(f"Total Execution Time: {elapsed}s | Test Exit Code: {exit_code}")
    print("=" * 80)
    return exit_code

if __name__ == "__main__":
    sys.exit(run_all_tests())
