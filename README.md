# SMART CANTEEN — ONLINE ORDERING & REAL-TIME QUEUE MANAGEMENT SYSTEM

> **Intelligent Campus Canteen Management System with Real-Time Queue Optimization and Dynamic Pickup Scheduling**

---

## 1. Project Overview

The **Smart Canteen Platform** is an intelligent campus food service orchestration system that eliminates physical ordering queues, minimizes pickup counter waiting times, avoids peak-surge crowding, and optimizes kitchen workload.

Unlike standard static online ordering apps, this platform treats the campus canteen as a **real-time capacity-constrained service system**, continuously integrating:
- Live kitchen workload & cooking station throughput
- Virtual queue position with **Fair Aging Anti-Starvation Scoring**
- Dynamic ETA estimation based on preceding order complexity
- Dynamic capacity-aware pickup slot scheduling
- Atomic transactional inventory reservation (preventing overselling)
- Single-use cryptographic **HMAC-SHA256 QR pickup tokens**
- Real-time multi-channel WebSocket communication

---

## 2. System Architecture & Tech Stack

- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, Lucide Icons, QRCode.react.
- **Backend**: Python 3.9+, FastAPI, Pydantic v2, SQLAlchemy, Python-Jose (JWT), WebSockets.
- **Database**: PostgreSQL / Supabase with standard SQLite local testing engine, composite indexes, and RLS.
- **Real-Time Communication**: Multi-channel WebSocket broker (`order:{id}`, `queue:updates`, `kitchen:kds`, `admin:metrics`).

---

## 3. Quick Start Guide

### Prerequisites
- Python 3.9+
- Node.js 18+ and npm

### 3.1 Run the Python Backend
```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run backend API server (starts on http://localhost:8000)
uvicorn app.main:app --reload --port 8000
```
- API Documentation: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/health`

### 3.2 Run the Next.js Frontend
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server (starts on http://localhost:3000)
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## 4. Demo User Accounts

The system includes pre-seeded campus accounts and an instant **1-click Role Switcher** on the navigation bar:

| Role | Email | Password | Campus ID | Permissions |
|:---|:---|:---|:---|:---|
| **Student** | `student@campus.edu` | `campus123` | `STU-2024-001` | Menu browsing, cart, slot selection, digital payments, live order tracking, QR token. |
| **Kitchen Staff** | `staff@campus.edu` | `staff123` | `STF-KITCHEN-01` | Live Kitchen Display System (KDS Kanban), start prep, mark ready, pickup QR scanner terminal. |
| **Admin** | `admin@campus.edu` | `admin123` | `ADM-DIR-001` | Executive operations monitor, peak surge classifier, low-stock inventory, ML demand forecasting. |

---

## 5. Automated Verification & Concurrency Tests

To run the complete automated test suite and generate the Requirement Evidence Matrix:
```bash
cd backend
python test_runner.py
```
Or directly with pytest:
```bash
cd backend
pytest -v
```

All 10 critical operational concurrency scenarios (overselling prevention, double payments, duplicate clicks, replay attacks, slot saturation) are verified.

---

## 6. Project Documentation
- [System Architecture](docs/ARCHITECTURE.md)
- [API Specification](docs/API_SPECIFICATION.md)
- [Database Schema & Migrations](docs/DATABASE_SCHEMA.md)
- [Queue & Dynamic ETA Algorithms](docs/QUEUE_AND_ETA_ALGORITHMS.md)
- [Concurrency & Security Audit](docs/CONCURRENCY_AND_SECURITY.md)
- [Evaluation & KPI Benchmark](docs/EVALUATION_AND_KPIS.md)
