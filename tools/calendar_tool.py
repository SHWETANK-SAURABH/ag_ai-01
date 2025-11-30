"""Calendar tool for creating reminders and events."""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class CalendarTool:
    """Tool for calendar operations with mock support."""
    
    def __init__(self, dev_mode: bool = False):
        self.dev_mode = dev_mode
        self.name = "calendar_tool"
        self.reminders: List[Dict[str, Any]] = []
    
    def can_handle(self, intent: str) -> bool:
        """Check if tool can handle the intent."""
        keywords = ["calendar", "reminder", "schedule", "event"]
        return any(kw in intent.lower() for kw in keywords)
    
    def dry_run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate execution without making changes."""
        tasks = params.get("tasks", [])
        return {
            "tool": self.name,
            "action": f"Would create {len(tasks)} calendar reminders",
            "requires_confirmation": True,
            "safe": True
        }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute calendar reminder creation."""
        tasks = params.get("tasks", [])
        
        created = []
        for task in tasks:
            reminder = self._create_reminder(task)
            if reminder:
                self.reminders.append(reminder)
                created.append(reminder)
        
        logger.info(f"Created {len(created)} calendar reminders")
        
        return {
            "status": "success",
            "reminders_created": len(created),
            "reminders": created
        }
    
    def _create_reminder(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create a reminder from a task."""
        
        if self.dev_mode:
            logger.info(f"Mock: Would create calendar reminder for: {task.get('title')}")
        
        return {
            "id": f"reminder_{task.get('id')}",
            "title": task.get("title", "Reminder"),
            "due_date": task.get("due_date"),
            "description": f"Amount: {task.get('amount', 'N/A')}",
            "account": task.get("account", ""),
            "calendar": "Life Admin",
            "created_via": "mock" if self.dev_mode else "api"
        }
    
    def get_reminders(self) -> List[Dict[str, Any]]:
        """Get all created reminders."""
        return self.reminders