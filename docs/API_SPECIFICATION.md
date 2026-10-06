# Smart Canteen Orchestration Platform — API Specification

Base URL: `/api/v1`

## 1. Authentication (`/auth`)
- `POST /auth/register`: Register new student or staff member.
- `POST /auth/login`: Authenticate and receive signed JWT access token.
- `GET /auth/me`: Get current authenticated user profile.

## 2. Menu Management (`/menu`)
- `GET /menu/categories`: List all categories.
- `POST /menu/categories` *(Staff/Admin)*: Create new menu category.
- `GET /menu/items`: List items with filters (`category_id`, `veg_only`, `available_only`, `search`).
- `GET /menu/items/{id}`: Get single item details.
- `POST /menu/items` *(Admin)*: Create menu item.
- `PUT /menu/items/{id}` *(Staff/Admin)*: Update menu item price, prep time, or availability.

## 3. Pickup Slots (`/pickup`)
- `GET /pickup/slots`: List all active pickup slots with real-time capacity and saturation status.
- `GET /pickup/slots/recommended`: Get optimal slot recommendation based on lowest surge.
- `PUT /pickup/slots/{id}` *(Staff/Admin)*: Modify slot capacity or close slot.

## 4. Orders & Real-Time Tracking (`/orders`)
- `POST /orders`: Place order with atomic inventory reservation, dynamic ETA calculation, and cryptographic QR token generation.
- `GET /orders/my`: Get all orders belonging to authenticated student.
- `GET /orders/{id}`: Get live order details, orders ahead, and dynamic ETA countdown.
- `POST /orders/verify-qr` *(Staff/Admin)*: Verify and consume cryptographic QR pickup token (Single-Use).
- `PUT /orders/{id}/status` *(Staff/Admin)*: Update order state (`PREPARING`, `READY`, `CANCELLED`).

## 5. Virtual Queue (`/queue`)
- `GET /queue/summary`: Get active queue length, workload classification, and aging scores.
- `POST /queue/recalculate`: Force recalculation of fair aging priority rankings.

## 6. Payments & Idempotency (`/payments`)
- `POST /payments/initiate`: Initiate digital payment with idempotency key protection.
- `POST /payments/verify`: Verify payment signature and transition order to `CONFIRMED`.
- `POST /payments/webhook`: Webhook listener for payment gateway callbacks.
- `GET /payments/{id}`: Get payment status.

## 7. Inventory (`/inventory`)
- `GET /inventory/logs` *(Staff/Admin)*: Audit trail of stock reservations, restocks, and adjustments.
- `GET /inventory/low-stock` *(Staff/Admin)*: Items below threshold (&le; 10 units).
- `POST /inventory/update` *(Staff/Admin)*: Add restock batch or adjust wastage.

## 8. Kitchen Display System (`/kitchen`)
- `GET /kitchen/orders` *(Staff/Admin)*: Kanban orders list (Queued, Preparing, Ready).
- `POST /kitchen/orders/{id}/start-prep` *(Staff/Admin)*: Move order to PREPARING.
- `POST /kitchen/orders/{id}/mark-ready` *(Staff/Admin)*: Move order to READY & send student alert.

## 9. Admin & Analytics (`/admin`, `/analytics`)
- `GET /admin/metrics` *(Admin/Staff)*: Live operational KPIs and throughput telemetry.
- `GET /admin/bottlenecks` *(Admin/Staff)*: Logged bottleneck alarms and resolutions.
- `GET /analytics/forecast` *(Admin/Staff)*: ML demand forecasts for upcoming 15m, 30m, and 1h intervals.

## 10. Real-Time Multi-Channel WebSockets (`/ws/{channel}`)
- `/ws/order:{id}`: Student live tracking channel.
- `/ws/queue:updates`: Queue position shifts and dynamic ETA recalibrations.
- `/ws/kitchen:kds`: Kitchen Display Kanban order stream.
- `/ws/admin:metrics`: Live surge classification and throughput updates.
