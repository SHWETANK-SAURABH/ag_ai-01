"""Task storage tool for persisting tasks and reminders."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class TaskStoreTool:
    """Tool for storing and retrieving tasks."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.name = "task_store"
        self.storage_path = storage_path or Path("data/tasks.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.tasks: List[Dict[str, Any]] = self._load_tasks()
    
    def can_handle(self, intent: str) -> bool:
        """Check if tool can handle the intent."""
        keywords = ["store", "save", "task", "reminder", "database"]
        return any(kw in intent.lower() for kw in keywords)
    
    def dry_run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate execution without making changes."""
        bills = params.get("bills", [])
        return {
            "tool": self.name,
            "action": f"Would store {len(bills)} tasks to database",
            "safe": True
        }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task storage."""
        bills = params.get("bills", [])
        
        stored_count = 0
        for bill in bills:
            task = self._create_task_from_bill(bill)
            if task:
                self._add_task(task)
                stored_count += 1
        
        self._save_tasks()
        logger.info(f"Stored {stored_count} tasks")
        
        return {
            "status": "success",
            "stored_count": stored_count,
            "total_tasks": len(self.tasks)
        }
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Retrieve all stored tasks."""
        return self.tasks
    
    def get_upcoming_tasks(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get tasks due within specified days."""
        upcoming = []
        now = datetime.now()
        
        for task in self.tasks:
            due_date = task.get("due_date")
            if due_date:
                try:
                    due_dt = datetime.fromisoformat(due_date)
                    days_until = (due_dt - now).days
                    if 0 <= days_until <= days:
                        upcoming.append(task)
                except:
                    pass
        
        return sorted(upcoming, key=lambda t: t.get("due_date", ""))
    
    def _create_task_from_bill(self, bill: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Convert a parsed bill into a task."""
        
        due_date = bill.get("due_date")
        if not due_date or due_date == "unknown":
            return None
        
        # Parse date string to ISO format
        due_date_iso = self._parse_date_to_iso(due_date)
        
        return {
            "id": f"task_{bill.get('id', datetime.now().timestamp())}",
            "type": "bill_payment",
            "title": f"Pay {bill.get('description', 'Bill')}",
            "amount": bill.get("amount", "unknown"),
            "due_date": due_date_iso,
            "account": bill.get("account", ""),
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "metadata": bill
        }
    
    def _parse_date_to_iso(self, date_str: str) -> str:
        """Parse various date formats to ISO format."""
        
        # Try common formats
        formats = [
            "%B %d, %Y",      # December 15, 2024
            "%b %d, %Y",      # Dec 15, 2024
            "%Y-%m-%d",       # 2024-12-15
            "%m/%d/%Y",       # 12/15/2024
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.isoformat()
            except:
                continue
        
        # Return original if parsing fails
        return date_str
    
    def _add_task(self, task: Dict[str, Any]) -> None:
        """Add a task to the store."""
        # Check for duplicates
        for existing in self.tasks:
            if existing.get("id") == task.get("id"):
                return
        
        self.tasks.append(task)
    
    def _load_tasks(self) -> List[Dict[str, Any]]:
        """Load tasks from storage."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load tasks: {e}")
        
        return []
    
    def _save_tasks(self) -> None:
        """Save tasks to storage."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.tasks, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save tasks: {e}")