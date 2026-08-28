# Mine Subsidence Monitoring - Notification Architecture

## Changes Made
1. **Connectivity Manager Service**
   - Created `ConnectivityManager` to track `internet_online`, `cellular_available`, `gateway_online`, `email_reachable`, and `sms_reachable`.
   - Added `/api/notifications/connectivity` and `/api/notifications/connectivity/override` endpoints for testing.

2. **Offline-First Notification Queue**
   - Refactored `NotificationService` to queue messages in the PostgreSQL `notification_queue` table *before* attempting delivery.
   - If the system is offline, alerts are stored in `WAITING_FOR_INTERNET` (Email) or `WAITING_FOR_NETWORK` (SMS) states.
   - Added idempotency checks: before queuing an alert, it verifies if an alert with the same `alert_id` and `recipient` is already `SENT` or `DELIVERED`.
   - Added a `process_notification_queue()` background task to automatically retry delivery on connectivity restoration.
   - Replaced SMTP with **EmailJS** API for email delivery (tracks real success/failure states).
   - Integrated Twilio (SMS provider) abstraction. For the prototype without credentials, it falls back to a clean `PENDING_MANUAL_FALLBACK` state rather than faking success.

3. **Notification Preferences**
   - Updated the `ResponsiblePerson` PostgreSQL model to persist `sms_notifications`, `email_notifications`, and `minimum_alert_priority`.

4. **Notifications UI Panel**
   - Added a brand new **Notifications & Connectivity Dashboard** (`/app/notifications`).
   - Displays real-time hardware and network health (Internet, Cellular, Gateway, Email Service).
   - Renders a living log of the `notification_queue` history (QUEUED, SENT, WAITING, FAILED).
   - Exposes a manual "Run Test Alert" button and "Force Queue Process" button.

## What Was Tested
- Simulated dropping internet and triggering a critical test alert.
- Simulated dropping cellular network.
- Restored connectivity and triggered the queue processor.

## Validation Results
- **TEST 1 (Internet ON, Cellular ON)**: Handled properly. Email fails with explicit missing credentials (not faked), SMS enters fallback.
- **TEST 2 (Internet OFF, Cellular ON)**: Email correctly queued as `WAITING_FOR_INTERNET`.
- **TEST 3 (Internet OFF, Cellular OFF)**: Both channels queued locally for offline handling.
- **TEST 4 (Restoration)**: Queue processed successfully, marking exhausted retries as `FAILED_MAX_RETRIES`.
- Duplicate prevention verified (no double-sends for the same alert ID).
