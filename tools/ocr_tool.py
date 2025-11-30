"""OCR tool for extracting text from documents (with mock)."""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class OCRTool:
    """Tool for OCR text extraction with mock support."""
    
    def __init__(self, dev_mode: bool = False):
        self.dev_mode = dev_mode
        self.name = "ocr_tool"
    
    def can_handle(self, intent: str) -> bool:
        """Check if tool can handle the intent."""
        keywords = ["scan", "ocr", "read", "extract text", "inbox"]
        return any(kw in intent.lower() for kw in keywords)
    
    def dry_run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate execution without making changes."""
        source = params.get("source", "unknown")
        return {
            "tool": self.name,
            "action": f"Would scan text from: {source}",
            "estimated_items": 5 if source == "inbox" else 3,
            "safe": True
        }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute OCR extraction."""
        source = params.get("source", "inbox")
        
        if self.dev_mode or source == "inbox":
            return self._mock_scan_inbox()
        
        logger.info(f"Scanning source: {source}")
        # Real OCR would go here
        return {"status": "success", "items": [], "count": 0}
    
    def _mock_scan_inbox(self) -> Dict[str, Any]:
        """Mock inbox scanning for development."""
        from simulated_data.inbox_samples import get_mock_inbox
        
        messages = get_mock_inbox()
        logger.info(f"Mock: Scanned {len(messages)} inbox messages")
        
        return {
            "status": "success",
            "source": "inbox",
            "items": messages,
            "count": len(messages)
        }