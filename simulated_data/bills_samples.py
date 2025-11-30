"""Mock bill documents for OCR and parsing testing."""

from typing import List, Dict


def get_mock_bills() -> List[Dict[str, str]]:
    """Generate mock bill documents as text (simulating OCR output)."""
    
    return [
        {
            "id": "bill_001",
            "type": "utility",
            "ocr_text": """
WATER UTILITY COMPANY
Account Number: WU-334455
Statement Date: November 28, 2024

Current Charges
Water Usage: $45.30
Sewer Service: $32.10
Environmental Fee: $5.00
-----------------------------
Total Amount Due: $82.40

DUE DATE: December 22, 2024

Please remit payment by mail or online.
            """.strip()
        },
        {
            "id": "bill_002",
            "type": "subscription",
            "ocr_text": """
STREAMING SERVICE PRO
Invoice #INV-2024-1145

Subscription: Premium Family Plan
Billing Period: Dec 1 - Dec 31, 2024
Amount: $17.99

Next Billing Date: January 1, 2025

Your payment method will be charged automatically.
            """.strip()
        },
        {
            "id": "bill_003",
            "type": "medical",
            "ocr_text": """
MEDICAL CENTER
Patient Statement

Patient ID: MC-998877
Service Date: November 15, 2024
Provider: Dr. Johnson

Services Rendered:
Office Visit - $150.00
Lab Work - $85.00
-----------------------------
Total Charges: $235.00
Insurance Paid: $180.00
-----------------------------
Patient Balance: $55.00

PLEASE PAY BY: December 30, 2024

Questions? Call (555) 123-4567
            """.strip()
        }
    ]