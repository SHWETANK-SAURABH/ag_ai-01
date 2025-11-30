"""Main entry point for Life Admin Task Automator."""

import logging
from config import config
from tools.gemini_client import GeminiClient
from tools.ocr_tool import OCRTool
from tools.bill_parser import BillParserTool
from tools.task_store import TaskStoreTool
from tools.calendar_tool import CalendarTool
from tools.notification_tool import NotificationTool
from memory.vector_store import VectorStore
from memory.memory_store import MemoryStore
from agents.planner import Planner
from agents.agent_controller import AgentController

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def initialize_system():
    """Initialize all system components."""
    
    logger.info(f"Initializing {config.APP_NAME}")
    logger.info(f"Mode: {config.get_mode_status()}")
    
    # Initialize Gemini client
    gemini_client = GeminiClient(
        api_key=config.GEMINI_API_KEY,
        model=config.GEMINI_MODEL,
        dev_mode=config.DEV_MODE
    )
    
    # Initialize tools
    ocr_tool = OCRTool(dev_mode=config.DEV_MODE)
    bill_parser = BillParserTool(gemini_client=gemini_client)
    task_store = TaskStoreTool()
    calendar_tool = CalendarTool(dev_mode=config.DEV_MODE)
    notification_tool = NotificationTool(dev_mode=config.DEV_MODE)
    
    tools = [ocr_tool, bill_parser, task_store, calendar_tool, notification_tool]
    
    # Initialize memory
    vector_store = VectorStore()
    memory_store = MemoryStore()
    
    # Initialize agents
    planner = Planner(gemini_client)
    agent = AgentController(planner, tools)
    
    return {
        "gemini": gemini_client,
        "tools": {
            "ocr": ocr_tool,
            "bill_parser": bill_parser,
            "task_store": task_store,
            "calendar": calendar_tool,
            "notification": notification_tool
        },
        "memory": {
            "vector": vector_store,
            "memory": memory_store
        },
        "agent": agent,
        "planner": planner
    }


def demo_parse_bill(system):
    """Demo: Parse bills and extract information."""
    
    print("\n" + "="*60)
    print("DEMO: Parse Bills")
    print("="*60 + "\n")
    
    from simulated_data.bills_samples import get_mock_bills
    
    bills = get_mock_bills()
    bill_parser = system["tools"]["bill_parser"]
    
    result = bill_parser.execute({"items": [{"body": b["ocr_text"], "id": b["id"]} for b in bills]})
    
    print(f"Parsed {result['count']} bills:\n")
    for bill in result["bills"]:
        print(f"  • {bill['description']}")
        print(f"    Amount: {bill['amount']}")
        print(f"    Due: {bill['due_date']}")
        print(f"    Account: {bill['account']}\n")


def demo_scan_inbox(system):
    """Demo: Scan inbox and process messages."""
    
    print("\n" + "="*60)
    print("DEMO: Scan Inbox")
    print("="*60 + "\n")
    
    ocr_tool = system["tools"]["ocr"]
    result = ocr_tool.execute({"source": "inbox"})
    
    print(f"Scanned {result['count']} messages:\n")
    for msg in result["items"][:3]:
        print(f"  • From: {msg['from']}")
        print(f"    Subject: {msg['subject']}")
        print(f"    Date: {msg['date']}\n")


def demo_vector_search(system):
    """Demo: Vector search over stored documents."""
    
    print("\n" + "="*60)
    print("DEMO: Vector Search")
    print("="*60 + "\n")
    
    vector_store = system["memory"]["vector"]
    
    # Add some sample documents
    from simulated_data.bills_samples import get_mock_bills
    
    bills = get_mock_bills()
    for bill in bills:
        vector_store.add_document(
            doc_id=bill["id"],
            text=bill["ocr_text"],
            metadata={"type": bill["type"]}
        )
    
    # Search
    query = "water bill due date"
    results = vector_store.search(query, top_k=2)
    
    print(f"Search query: '{query}'\n")
    print(f"Found {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        doc = result["document"]
        score = result["score"]
        print(f"  {i}. Document: {doc['id']} (score: {score:.3f})")
        print(f"     Type: {doc['metadata'].get('type')}")
        print(f"     Preview: {doc['text'][:100]}...\n")


def demo_full_workflow(system):
    """Demo: Complete workflow from inbox to notifications."""
    
    print("\n" + "="*60)
    print("DEMO: Full Workflow")
    print("="*60 + "\n")
    
    agent = system["agent"]
    
    # Execute full workflow
    prompt = "Scan my inbox, parse any bills, create tasks, and send notifications for upcoming due dates"
    
    result = agent.execute_prompt(prompt, auto_confirm=True)
    
    print("\n" + "="*60)
    print("Workflow Summary")
    print("="*60 + "\n")
    
    for step_result in result["results"]:
        status = step_result["status"]
        step_num = step_result["step"]
        
        if status == "success":
            print(f"✅ Step {step_num}: {status}")
        else:
            print(f"❌ Step {step_num}: {status}")
    
    # Show stored tasks
    task_store = system["tools"]["task_store"]
    upcoming = task_store.get_upcoming_tasks(days=30)
    
    print(f"\n📋 Upcoming Tasks ({len(upcoming)}):\n")
    for task in upcoming[:5]:
        print(f"  • {task['title']}")
        print(f"    Due: {task['due_date']}")
        print(f"    Amount: {task.get('amount', 'N/A')}\n")


def main():
    """Main entry point."""
    
    print("\n" + "="*60)
    print(f"  {config.APP_NAME}")
    print(f"  Mode: {config.get_mode_status()}")
    print("="*60)
    
    # Initialize system
    system = initialize_system()
    
    # Run demos
    demo_scan_inbox(system)
    demo_parse_bill(system)
    demo_vector_search(system)
    demo_full_workflow(system)
    
    print("\n" + "="*60)
    print("All demos completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()