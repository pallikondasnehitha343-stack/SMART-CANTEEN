# Concurrency Validation & Security Audit

## 1. Concurrency Scenarios & Execution Proof

All 10 critical operational concurrency scenarios have been programmatically implemented, stress-tested, and verified:

| # | Concurrency Scenario | Engineering Mechanism | Test Verification | Result |
|---|----------------------|-----------------------|-------------------|:------:|
| 1 | **Simultaneous Purchase of Last Item** | Transactional atomic inventory decrement & database row locks. | `test_concurrency_01_last_item_overselling_prevention` | **PASS** |
| 2 | **Double Payment Callbacks** | Payment state idempotency checking against existing transaction record. | `test_concurrency_02_double_payment_callbacks_same_order` | **PASS** |
| 3 | **Double-Clicking Pay Button** | Unique `idempotency_key` enforcement returning the identical transaction. | `test_concurrency_03_double_clicking_payment_button` | **PASS** |
| 4 | **Duplicate Order at Zero Stock** | Atomic validation rejects order when stock reaches 0. | `test_concurrency_04_duplicate_order_submission_with_zero_stock` | **PASS** |
| 5 | **Simultaneous Staff Updates** | Deterministic state machine checks and atomic status updates. | `test_concurrency_05_two_staff_members_updating_same_order` | **PASS** |
| 6 | **Pickup QR Scanned Twice** | Single-use `is_qr_used` flag atomically set to 1 upon first verification; second attempt triggers 409 Conflict. | `test_concurrency_06_pickup_qr_scanned_twice` | **PASS** |
| 7 | **Premature QR Scan (Before Ready)** | Rejects pickup verification if order is in `QUEUED` or `PREPARING` states. | `test_concurrency_07_pickup_qr_used_while_not_ready` | **PASS** |
| 8 | **Pickup Slot Becoming Full** | Atomic capacity checking rejects overbooking when `booked_count >= capacity`. | `test_concurrency_08_pickup_slot_becoming_full` | **PASS** |
| 9 | **Kitchen Workload Dynamic ETA Shift** | ETA engine dynamically reflects cumulative workload of all preceding active orders. | `test_concurrency_09_kitchen_workload_changing_dynamic_eta` | **PASS** |
| 10| **Peak Order Influx Bursts** | Sequential monotonic queue position assignments with unique token numbers. | `test_concurrency_10_multiple_orders_peak_burst` | **PASS** |

---

## 2. Security Controls & RBAC Audit

1. **Authentication & Password Hashing**: Passwords stored as salted HMAC-SHA256 hashes.
2. **Role-Based Access Control (RBAC)**: Enforced via FastAPI dependencies (`STUDENT`, `STAFF`, `ADMIN`).
3. **Cryptographic QR Tokens**: HMAC-SHA256 signatures generated using server-side secret keys. Tampered tokens are rejected.
4. **Idempotency Protection**: Replay and double-charge protection using UUID idempotency keys.
5. **Database Integrity**: Negative stock quantities and overbooked slots strictly prohibited via database check constraints and validation triggers.
