# Smart Canteen Orchestration Platform — Architecture Document

## 1. System Vision & Positioning

**Intelligent Campus Canteen Management System with Real-Time Queue Optimization and Dynamic Pickup Scheduling**

The Smart Canteen platform transforms campus food service by treating the canteen as a capacity-constrained, real-time cyber-physical service system. It integrates online ordering, digital payments, virtual queue management, dynamic pickup slots, live dynamic ETA estimation, kitchen workload management, transactional inventory safety, and cryptographic QR pickup verification.

---

## 2. High-Level Architecture

```
                                  CAMPUS USERS
           ┌────────────────────────────┼────────────────────────────┐
           ▼                            ▼                            ▼
   [ Student Mobile UI ]       [ Kitchen Staff KDS ]     [ Admin Console / Scanner ]
           │                            │                            │
           └────────────────────────────┼────────────────────────────┘
                                        │ (HTTP REST / WebSockets)
                                        ▼
                  ┌───────────────────────────────────────────┐
                  │          NEXT.JS 14 FRONTEND              │
                  │   App Router • TypeScript • Tailwind CSS  │
                  └─────────────────────┬─────────────────────┘
                                        │ (JSON API / WebSocket)
                                        ▼
                  ┌───────────────────────────────────────────┐
                  │       FASTAPI BACKEND CORE ENGINE         │
                  │  Auth (JWT/RBAC) • Pydantic v2 • Security │
                  ├───────────────────────────────────────────┤
                  │ 1. Deterministic Dynamic ETA Engine       │
                  │ 2. Fair Aging Priority Queue Optimizer    │
                  │ 3. Capacity-Aware Pickup Slot Allocator   │
                  │ 4. Transactional Stock Reservation Engine │
                  │ 5. Idempotent Payment State Machine       │
                  │ 6. Cryptographic HMAC QR Token Service    │
                  │ 7. Peak Surge Classifier & ML Forecaster  │
                  │ 8. Multi-Channel WebSocket Broker         │
                  └─────────────────────┬─────────────────────┘
                                        │ (SQLAlchemy ORM / Raw SQL)
                                        ▼
                  ┌───────────────────────────────────────────┐
                  │         DATABASE RELATIONAL LAYER         │
                  │        PostgreSQL / Supabase / SQLite     │
                  │   - Composite Performance Indexes         │
                  │   - Row Level Security (RLS)              │
                  │   - Check Constraints & Foreign Keys      │
                  │   - Atomic Audit Logs                     │
                  └───────────────────────────────────────────┘
```

---

## 3. Order Lifecycle State Machine

An order strictly transitions through the following deterministic states:

```
[ CREATED ]
     │
     ▼ (Item stock & pickup slot atomically reserved)
[ PAYMENT_PENDING ]
     │
     ├─────────────► [ CANCELLED / REFUNDED ] (Stock & Slot auto-restored)
     ▼ (Payment verified with HMAC signature & Idempotency Key)
[ CONFIRMED ]
     │
     ▼ (Enqueued into Virtual Queue with Aging Score)
[ QUEUED ]
     │
     ▼ (Assigned to cooking station)
[ PREPARING ]
     │
     ▼ (Actual prep completed; Push notification & live countdown triggers)
[ READY ]
     │
     ▼ (Tamper-proof QR token scanned at pickup counter)
[ PICKED_UP ]
```

---

## 4. Mathematical Engine Specifications

### 4.1 Dynamic ETA Derivation
$$\text{Workload}(O) = \sum_{i \in \text{Items}} \text{PrepTime}_i \times \left(1.0 + 0.4 \times (\text{Qty}_i - 1)\right) \times \text{Complexity}_i$$

$$\text{Preceding Queue Workload} = \sum_{P \in \text{Active Orders Ahead}} \text{Workload}(P)$$

$$\text{Effective Kitchen Capacity} = \text{Active Stations} \times \text{Throughput Rate per Min}$$

$$\text{Dynamic ETA (mins)} = \max\left(5, \left\lceil \frac{\text{Preceding Queue Workload}}{\text{Effective Kitchen Capacity} \times 10.0} + \text{Intrinsic Prep Time} + \text{Buffer} \right\rceil\right)$$

### 4.2 Fair Aging Anti-Starvation Priority Score
$$\text{Waiting Time (mins)} = \frac{t_{\text{now}} - t_{\text{queue\_entry}}}{60.0}$$
$$\text{Aging Bonus} = \text{Waiting Time} \times \text{Aging Bonus per Min}$$
$$\text{Priority Score} = 100.0 + (w_1 \cdot \text{Aging Bonus}) + (w_2 \cdot \text{Urgency}) - (w_3 \cdot \text{Complexity})$$

*Guaranteed Property*: Because $\text{Aging Bonus}$ increases monotonically over time, any older waiting order will strictly surpass newly arrived orders regardless of small differences in complexity, mathematically preventing starvation.
