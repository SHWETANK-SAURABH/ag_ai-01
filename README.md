# Life Admin Task Automator

Small demo app that scans inbox-like data, parses bills, stores tasks, and demonstrates a simple agent workflow. The project can run in DEVELOPMENT (mock) mode or PRODUCTION mode backed by the Google Generative AI (Gemini) SDK.

**Quick start**

- Copy `.env.example` to `.env` and set `GEMINI_API_KEY` if you want to use the live Gemini API. Do NOT commit `.env`.
- Install dependencies and run the demos.

Install dependencies (Windows PowerShell):
```powershell
py -3 -m pip install --upgrade pip
py -3 -m pip install -r .\requirements.txt
```

Run demos:
```powershell
py -3 -u .\main.py
```

To run with a real Gemini API key for production mode (replace placeholder):
```powershell
# set for this session
$env:GEMINI_API_KEY = 'your_real_api_key_here'
py -3 -u .\main.py

# or create a .env file in the project root with:
# GEMINI_API_KEY=your_real_api_key_here
```

Notes
- The app auto-detects development mode when `GEMINI_API_KEY` is missing.
- Keep API keys out of VCS. `.gitignore` already excludes `.env` and the `data/` and `memory/storage/` folders used for local storage.

Contributing
- If you'd like me to add a simple test harness, CI pipeline, or Dockerfile adjustments for deployment, tell me which you'd prefer and I can add it.
# Life Admin Task Automator

An intelligent agent system that automates life administration tasks by reading emails, parsing bills, extracting due dates, creating reminders, and sending notifications.

## Features

- 📧 **Inbox Scanning**: Automatically scans and processes inbox messages
- 📄 **Bill Parsing**: Extracts key information from bills (amount, due date, account)
- 📅 **Task Management**: Creates and stores tasks with due dates
- 🔔 **Smart Notifications**: Sends alerts for upcoming due dates
- 🧠 **Vector Search**: Semantic search over documents and bills
- 🤖 **AI Planning**: Uses Gemini API for intelligent task planning
- 🔄 **Dev Mode**: Full mock support for development without API credentials

## Project Structure
```
life_admin_task_automator/
├── main.py                 # Entry point with demos
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── agents/                 # Planning and orchestration
│   ├── planner.py          # AI-powered plan generation
│   └── agent_controller.py # Execution orchestration
├── tools/                  # Task execution tools
│   ├── gemini_client.py    # Gemini API wrapper with mock
│   ├── ocr_tool.py         # Document scanning
│   ├── bill_parser.py      # Bill information extraction
│   ├── task_store.py       # Task persistence
│   ├── calendar_tool.py    # Calendar integration
│   └── notification_tool.py # Notification system
├── memory/                 # Memory and storage
│   ├── vector_store.py     # Semantic search
│   └── memory_store.py     # Conversation history
└── simulated_data/         # Mock data for development
    ├── inbox_samples.py
    └── bills_samples.py