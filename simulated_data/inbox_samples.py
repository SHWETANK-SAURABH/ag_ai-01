"""Mock inbox messages for development and testing."""

from typing import List, Dict
from datetime import datetime, timedelta


def get_mock_inbox() -> List[Dict[str, str]]:
    """Generate mock inbox messages with bills and reminders."""
    
    today = datetime.now()
    
    return [
        {
            "id": "msg_001",
            "from": "billing@electric-company.com",
            "subject": "Your Electricity Bill - Due Dec 15",
            "date": (today - timedelta(days=2)).isoformat(),
            "body": """
Dear Customer,

Your electricity bill for November is now available.

Amount Due: $127.50
Due Date: December 15, 2024
Account Number: EC-998877

Please pay by the due date to avoid late fees.

Thank you,
Electric Company
            """.strip()
        },
        {
            "id": "msg_002",
            "from": "support@internet-isp.com",
            "subject": "Internet Service Bill - Payment Required",
            "date": (today - timedelta(days=1)).isoformat(),
            "body": """
Hello,

Your monthly internet service bill is ready.

Amount: $89.99
Due: December 10, 2024
Account: ISP-445566

Pay online at www.internet-isp.com/pay

Best regards,
ISP Support Team
            """.strip()
        },
        {
            "id": "msg_003",
            "from": "noreply@creditcard-bank.com",
            "subject": "Credit Card Statement Available",
            "date": (today - timedelta(hours=12)).isoformat(),
            "body": """
Your credit card statement is now available.

Statement Period: Nov 1 - Nov 30, 2024
Total Amount Due: $543.21
Minimum Payment: $25.00
Payment Due Date: December 20, 2024

Log in to view your full statement.
            """.strip()
        },
        {
            "id": "msg_004",
            "from": "reminders@dentist-office.com",
            "subject": "Appointment Reminder - Dr. Smith",
            "date": today.isoformat(),
            "body": """
Appointment Reminder

Patient: John Doe
Date: December 18, 2024
Time: 2:30 PM
Location: 123 Main St, Suite 200

Please arrive 10 minutes early. Call us if you need to reschedule.
            """.strip()
        },
        {
            "id": "msg_005",
            "from": "insurance@auto-insurance.com",
            "subject": "Policy Renewal Notice",
            "date": today.isoformat(),
            "body": """
Your auto insurance policy is up for renewal.

Policy Number: AI-778899
Renewal Date: January 5, 2025
Premium Amount: $1,250.00

Review and renew your policy to avoid coverage gaps.
            """.strip()
        }
    ]