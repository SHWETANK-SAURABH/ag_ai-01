"""Bill parser tool for extracting structured data from bills."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)


class BillParserTool:
    """Tool for parsing bills and extracting key information."""
    
    def __init__(self, gemini_client=None):
        self.gemini_client = gemini_client
        self.name = "bill_parser"
    
    def can_handle(self, intent: str) -> bool:
        """Check if tool can handle the intent."""
        keywords = ["parse", "bill", "extract", "due date", "amount"]
        return any(kw in intent.lower() for kw in keywords)
    
    def dry_run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate execution without making changes."""
        items = params.get("items", [])
        return {
            "tool": self.name,
            "action": f"Would parse {len(items)} items for bills and due dates",
            "safe": True
        }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute bill parsing."""
        items = params.get("items", [])
        
        if not items:
            from simulated_data.bills_samples import get_mock_bills
            bills = get_mock_bills()
            items = [{"body": bill["ocr_text"], "id": bill["id"]} for bill in bills]
        
        parsed_bills = []
        
        for item in items:
            text = item.get("body", "") or item.get("ocr_text", "")
            if not text:
                continue
            
            parsed = self._parse_bill_text(text, item.get("id", "unknown"))
            if parsed:
                parsed_bills.append(parsed)
        
        logger.info(f"Parsed {len(parsed_bills)} bills successfully")
        
        return {
            "status": "success",
            "bills": parsed_bills,
            "count": len(parsed_bills)
        }
    
    def _parse_bill_text(self, text: str, bill_id: str) -> Optional[Dict[str, Any]]:
        """Parse a single bill text and extract key information."""
        
        # Use Gemini if available
        if self.gemini_client and not self.gemini_client.dev_mode:
            try:
                entities = self.gemini_client.extract_entities(
                    text,
                    ["amount", "due_date", "account_number", "company_name"]
                )
                if entities:
                    return {
                        "id": bill_id,
                        "amount": entities.get("amount", "unknown"),
                        "due_date": entities.get("due_date", "unknown"),
                        "account": entities.get("account_number", ""),
                        "company": entities.get("company_name", ""),
                        "description": self._extract_description(text),
                        "raw_text": text[:200]
                    }
            except Exception as e:
                logger.warning(f"Gemini extraction failed: {e}, using fallback")
        
        # Fallback to regex parsing
        amount = self._extract_amount(text)
        due_date = self._extract_date(text)
        account = self._extract_account(text)
        
        if amount or due_date:
            return {
                "id": bill_id,
                "amount": amount or "unknown",
                "due_date": due_date or "unknown",
                "account": account or "",
                "description": self._extract_description(text),
                "raw_text": text[:200]
            }
        
        return None
    
    def _extract_amount(self, text: str) -> Optional[str]:
        """Extract monetary amount from text."""
        patterns = [
            r'(?:total|amount|balance|due|payment).*?\$\s*([\d,]+\.?\d*)',
            r'\$\s*([\d,]+\.?\d*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"${match.group(1)}"
        
        return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract due date from text."""
        patterns = [
            r'(?:due|pay by|payment due).*?:?\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
            r'([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_account(self, text: str) -> Optional[str]:
        """Extract account number from text."""
        patterns = [
            r'account\s*(?:number|#)?\s*:?\s*([A-Z0-9-]+)',
            r'([A-Z]{2}-\d{6})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_description(self, text: str) -> str:
        """Extract a brief description from the bill."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Look for company name or service type
        for line in lines[:5]:
            if any(word in line.lower() for word in ['bill', 'statement', 'invoice', 'company', 'service']):
                return line[:100]
        
        return lines[0][:100] if lines else "Bill"