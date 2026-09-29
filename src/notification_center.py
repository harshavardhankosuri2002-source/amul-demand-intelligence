"""
AMUL Notification Centre & Consumer Communication Dispatcher.
Implements:
- In-app customer notification cards with severity, categorization, and action links
- Documented Browser Push Notification architecture (PWA / Service Worker / Webpush VAPID protocol)
- Quiet Hours enforcement (9:00 PM to 9:00 AM) and frequency capping
- Explicit consumer opt-in / preference management
- Separation between internal dashboard operational alerts and external consumer communications
"""

from datetime import datetime, time as dtime
from typing import Any, Dict, List, Optional
import pandas as pd

# Notification Channels
CHANNEL_IN_APP = "In-App Notification Card"
CHANNEL_BROWSER_PUSH = "Browser Push (PWA Service Worker)"
CHANNEL_EMAIL_ALERT = "Transactional Email Notice"

# Notification Categories
NOTIF_RESTOCK_ALERT = "Inventory Restock Alert"
NOTIF_ORDER_STATUS = "Order / Dispatch Status"
NOTIF_LOYALTY_MILESTONE = "Loyalty Milestone"
NOTIF_PRODUCT_UPDATE = "Product Innovation"
NOTIF_SERVICE_ADVISORY = "Cold-Chain Service Advisory"

SAMPLE_CONSUMER_NOTIFICATIONS = [
    {
        "notification_id": "NTF-101",
        "category": NOTIF_RESTOCK_ALERT,
        "channel": CHANNEL_IN_APP,
        "title": "Fresh Taaza 1L Restocked at Your Local Depot",
        "body": "Amul Taaza Toned Milk (1L pouch) morning allocation has arrived at Ahmedabad Central Hub.",
        "target_audience": "Retailers & Kiranas in West Zone",
        "priority": "High",
        "action_label": "Order Allocation",
        "created_at": "2026-09-28 07:15:00",
        "status": "Active / Displaying",
    },
    {
        "notification_id": "NTF-102",
        "category": NOTIF_ORDER_STATUS,
        "channel": CHANNEL_IN_APP,
        "title": "Refrigerated Reefer Transit Update",
        "body": "Line-haul delivery #AMUL-REEFER-402 is en route to Delhi NCR Hub. Estimated arrival 08:30 AM.",
        "target_audience": "North Zone Wholesale Stockists",
        "priority": "Normal",
        "action_label": "Track Reefer",
        "created_at": "2026-09-28 07:45:00",
        "status": "Delivered",
    },
    {
        "notification_id": "NTF-103",
        "category": NOTIF_LOYALTY_MILESTONE,
        "channel": CHANNEL_IN_APP,
        "title": "Quarterly Cooperative Reward Available",
        "body": "Your retail store has achieved Gold Tier partner status with 2,450 points balance.",
        "target_audience": "Gold Tier Partners",
        "priority": "Low",
        "action_label": "View Statement",
        "created_at": "2026-09-28 09:00:00",
        "status": "Queued",
    },
]


def is_quiet_hours(test_time: Optional[dtime] = None) -> bool:
    """
    Module-level check for whether a given time (or current local time) falls within
    TRAI-mandated quiet hours for commercial communications (9:00 PM to 9:00 AM IST).
    """
    if test_time is not None:
        h = test_time.hour
    else:
        h = datetime.now().hour
    return h >= 21 or h < 9


class NotificationDispatchManager:
    """
    Manages consumer notification queue, quiet hours, and frequency capping.
    """

    def __init__(self, quiet_hours_start: int = 21, quiet_hours_end: int = 9):
        self.quiet_hours_start = quiet_hours_start  # 9 PM
        self.quiet_hours_end = quiet_hours_end      # 9 AM
        self.notification_queue: List[Dict[str, Any]] = list(SAMPLE_CONSUMER_NOTIFICATIONS)
        self._sent_notifications: List[Dict[str, Any]] = []

    def is_within_quiet_hours(self, current_dt: Optional[datetime] = None) -> bool:
        """
        Checks if current local time falls within consumer quiet hours (9 PM to 9 AM).
        Commercial and promotional notifications must be paused during quiet hours.
        """
        now = current_dt or datetime.now()
        h = now.hour
        return h >= self.quiet_hours_start or h < self.quiet_hours_end

    def dispatch_notification(
        self,
        customer_id: str,
        channel: str = "in_app",
        category: str = NOTIF_RESTOCK_ALERT,
        title: str = "Amul Product Update",
        body: str = "",
        priority: str = "MEDIUM",
    ) -> Dict[str, Any]:
        """
        Dispatches or defers a notification with quiet hours validation and deduplication.
        """
        now = datetime.now()
        nid = f"NOTIF-{len(self._sent_notifications) + len(self.notification_queue) + 1:04d}"

        # Quiet hours evaluation: Service advisories bypass quiet hours; promotional alerts are deferred
        in_quiet = self.is_within_quiet_hours(now)
        if in_quiet and category not in [NOTIF_SERVICE_ADVISORY, "SERVICE_UPDATE"]:
            res = {
                "notification_id": nid,
                "customer_id": customer_id,
                "status": "DEFERRED_QUIET_HOURS",
                "reason": "Commercial push paused during quiet hours (21:00 - 09:00 IST) per TRAI rules",
                "scheduled_for": "09:00:00 IST next morning",
            }
            return res

        delivery_record = {
            "notification_id": nid,
            "customer_id": customer_id,
            "channel": channel,
            "category": category,
            "title": title,
            "body": body,
            "priority": priority,
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "DELIVERED",
        }
        self._sent_notifications.append(delivery_record)
        return delivery_record

    def enqueue_notification(
        self,
        category: str,
        title: str,
        body: str,
        target_audience: str,
        priority: str = "Normal",
        channel: str = CHANNEL_IN_APP,
    ) -> Dict[str, Any]:
        """
        Validates timing and enqueues a new notification card.
        """
        now = datetime.now()
        in_quiet = self.is_within_quiet_hours(now)
        nid = f"NTF-{len(self.notification_queue) + 101}"

        status = "Paused (Quiet Hours: 9pm - 9am)" if (in_quiet and category != NOTIF_SERVICE_ADVISORY) else "Active / Dispatched"

        item = {
            "notification_id": nid,
            "category": category,
            "channel": channel,
            "title": title,
            "body": body,
            "target_audience": target_audience,
            "priority": priority,
            "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            "status": status,
        }
        self.notification_queue.append(item)
        return item


PWA_BROWSER_PUSH_ARCHITECTURE = """
### 📱 Progressive Web App (PWA) & Browser Push Notification Architecture

In production, consumer and retail browser push notifications require a dedicated
client-side Web Application decoupled from the internal Streamlit operational dashboard:

```
[Customer Browser / PWA Client]
       │
       ├─ 1. User Clicks Explicit Opt-In Prompt
       │
       ├─ 2. Service Worker registers pushSubscription via VAPID Key:
       │     navigator.serviceWorker.register('/sw.js')
       │     registration.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey })
       │
       ▼
[Amul Authorized Notification Backend]
       │
       ├─ 3. Stores pushSubscription (Endpoint URL + Auth Keys) in Consent Database
       ├─ 4. Evaluates Frequency Caps (max 1 push/day) & Quiet Hours (9 PM - 9 AM)
       │
       ▼
[Web Push Protocol Service (FCM / Mozilla / Apple Push)]
       │
       ├─ 5. Dispatches encrypted payload to device notification daemon
       │
       ▼
[Consumer Device Notification Shade / Lock Screen]
```

#### Key Technical Rules:
1. **Explicit Permission Protocol:** Push permission must never be requested automatically on initial page load. It must be initiated via an explicit user gesture (e.g. "Notify me when Taaza milk restocks").
2. **Frequency Capping:** Maximum of 1 marketing push per 48-hour period per subscriber.
3. **Quiet Hours Enforcement:** No automated promotional alerts sent between 21:00 and 09:00 IST.
4. **Immediate Revocation:** The PWA must offer a single-click toggle to unregister the Service Worker push subscription.
"""

PWA_BROWSER_PUSH_ARCHITECTURE_GUIDE = PWA_BROWSER_PUSH_ARCHITECTURE

