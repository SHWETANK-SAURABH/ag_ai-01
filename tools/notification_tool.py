"""Notification tool for sending alerts and reminders."""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class NotificationTool:
    """Tool for sending notifications with mock support."""
    
    def __init__(self, dev_mode: bool = False):
        self.dev_mode = dev_mode
        self.name = "notification_tool"
        self.sent_notifications: List[Dict[str, Any]] = []
    
    def can_handle(self, intent: str) -> bool:
        """Check if tool can handle the intent."""
        keywords = ["notify", "notification", "alert", "remind", "send"]
        return any(kw in intent.lower() for kw in keywords)
    
    def dry_run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate execution without making changes."""
        tasks = params.get("tasks", [])
        return {
            "tool": self.name,
            "action": f"Would send notifications for {len(tasks)} tasks",
            "safe": True
            }
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute notification sending."""
        tasks = params.get("tasks", [])

        sent = []
        for task in tasks:
            if self._should_notify(task):
                notification = self._send_notification(task)
                if notification:
                    self.sent_notifications.append(notification)
                    sent.append(notification)

        logger.info(f"Sent {len(sent)} notifications")

        return {
            "status": "success",
            "notifications_sent": len(sent),
            "notifications": sent
        }

    def _should_notify(self, task: Dict[str, Any]) -> bool:
        """Determine if a task should trigger a notification."""

        due_date = task.get("due_date")
        if not due_date:
            return False

        try:
            due_dt = datetime.fromisoformat(due_date)
            days_until = (due_dt - datetime.now()).days

            # Notify if due within 7 days
            return 0 <= days_until <= 7
        except:
            return False

    def _send_notification(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Send a notification for a task."""

        message = self._format_notification_message(task)

        if self.dev_mode:
            logger.info(f"Mock notification: {message}")
            print(f"\n📢 NOTIFICATION: {message}\n")
        else:
            # Real notification service would go here
            logger.info(f"Sent notification: {message}")

        return {
            "id": f"notif_{datetime.now().timestamp()}",
            "task_id": task.get("id"),
            "message": message,
            "sent_at": datetime.now().isoformat(),
            "channel": "mock" if self.dev_mode else "push"
        }

    def _format_notification_message(self, task: Dict[str, Any]) -> str:
        """Format a notification message."""

        title = task.get("title", "Task")
        amount = task.get("amount", "")
        due_date = task.get("due_date", "")

        try:
            due_dt = datetime.fromisoformat(due_date)
            days_until = (due_dt - datetime.now()).days

            if days_until == 0:
                urgency = "DUE TODAY"
            elif days_until == 1:
                urgency = "Due tomorrow"
            else:
                urgency = f"Due in {days_until} days"
        except:
            urgency = "Due soon"

        if amount and amount != "unknown":
            return f"{urgency}: {title} - {amount}"
        else:
            return f"{urgency}: {title}"

    def get_sent_notifications(self) -> List[Dict[str, Any]]:
        """Get all sent notifications."""
        return self.sent_notifications