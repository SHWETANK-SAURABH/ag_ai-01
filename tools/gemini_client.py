"""Gemini API client with mock fallback for development."""

import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class GeminiClient:
    """Wrapper for Gemini API with development mode mock."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-pro", dev_mode: bool = False):
        self.api_key = api_key
        self.model = model
        self.dev_mode = dev_mode or not api_key
        self.client = None
        self._genai = None

        if not self.dev_mode:
            try:
                import google.generativeai as genai
                # Configure the SDK with the provided key
                try:
                    genai.configure(api_key=self.api_key)
                except Exception:
                    # Older/newer SDKs may use different config methods; ignore here
                    pass

                self._genai = genai

                # Detect common SDK surfaces and keep a reference
                if hasattr(genai, 'responses') and hasattr(genai.responses, 'create'):
                    # Newer SDK: use genai.responses.create
                    self.client = 'responses'
                elif hasattr(genai, 'generate_text'):
                    # Some versions expose a higher-level generate_text helper
                    self.client = 'generate_text'
                elif hasattr(genai, 'GenerativeModel'):
                    # Older or alternate surface
                    try:
                        self.client = genai.GenerativeModel(self.model)
                    except Exception:
                        self.client = None

                logger.info(f"Gemini client initialized (model: {self.model}, client: {self.client})")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}. Falling back to dev mode.")
                self.dev_mode = True

        if self.dev_mode:
            logger.info("Running in DEVELOPMENT mode with mock responses")
    
    def generate_plan(self, prompt: str) -> Dict[str, Any]:
        """Generate an execution plan from a prompt."""
        
        if self.dev_mode:
            return self._mock_generate_plan(prompt)
        
        try:
            full_prompt = f"""
You are a task planning assistant. Analyze the following request and create a step-by-step execution plan.
Return ONLY valid JSON with this structure:
{{
    "intent": "description of what user wants",
    "steps": [
        {{
            "step_number": 1,
            "tool": "tool_name",
            "action": "action description",
            "params": {{}},
            "requires_confirmation": true/false
        }}
    ]
}}

Request: {prompt}
"""
            text = self._call_model(full_prompt)
            # Extract JSON from markdown code blocks if present
            if not text:
                raise RuntimeError("Empty response from Gemini API")

            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            return json.loads(text)

        except Exception as e:
            logger.error(f"Gemini API error: {e}. Using mock fallback.")
            return self._mock_generate_plan(prompt)
            
            # Extract JSON from markdown code blocks if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            return json.loads(text)
        
        except Exception as e:
            logger.error(f"Gemini API error: {e}. Using mock fallback.")
            return self._mock_generate_plan(prompt)
    
    def extract_entities(self, text: str, entity_types: list[str]) -> Dict[str, Any]:
        """Extract specific entities from text."""
        
        if self.dev_mode:
            return self._mock_extract_entities(text, entity_types)
        
        try:
            prompt = f"""
Extract the following entities from the text: {', '.join(entity_types)}
Return ONLY valid JSON with the extracted entities.

Text: {text}
"""
            response_text = self._call_model(prompt)
            if not response_text:
                raise RuntimeError("Empty response from Gemini API")

            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            return json.loads(response_text)

        except Exception as e:
            logger.error(f"Gemini API error: {e}. Using mock fallback.")
            return self._mock_extract_entities(text, entity_types)

    def _call_model(self, prompt: str) -> str:
        """Call the underlying generative model using detected SDK surface.

        This method attempts to support multiple versions of the `google-generativeai`
        package by detecting available call surfaces and returning the textual
        content of the model response.
        """
        if not self._genai:
            raise RuntimeError("Generative AI SDK not initialized")

        try:
            # Newer SDK surface: genai.responses.create
            if self.client == 'responses' and hasattr(self._genai, 'responses'):
                resp = self._genai.responses.create(model=self.model, input=prompt)
                # Try to extract content from common locations
                if hasattr(resp, 'output') and resp.output:
                    # output may be a list of items with 'content'
                    out = resp.output
                    if isinstance(out, list) and len(out) > 0 and hasattr(out[0], 'content'):
                        return out[0].content
                    # Some SDKs return nested dicts
                    try:
                        return out[0]['content']
                    except Exception:
                        pass

                # Fallback to string conversion
                return str(resp)

            # Older helper: genai.generate_text
            if self.client == 'generate_text' and hasattr(self._genai, 'generate_text'):
                resp = self._genai.generate_text(model=self.model, prompt=prompt)
                # Some versions return an object with .text or .output
                if hasattr(resp, 'text'):
                    return resp.text
                try:
                    return str(resp)
                except Exception:
                    return ''

            # If self.client is a GenerativeModel instance
            if hasattr(self.client, 'generate_content'):
                resp = self.client.generate_content(prompt)
                if hasattr(resp, 'text'):
                    return resp.text
                return str(resp)

            raise RuntimeError('No supported client surface found in google.generativeai')
        except Exception as e:
            raise
            
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            return json.loads(text)
        
        except Exception as e:
            logger.error(f"Gemini API error: {e}. Using mock fallback.")
            return self._mock_extract_entities(text, entity_types)
    
    def _mock_generate_plan(self, prompt: str) -> Dict[str, Any]:
        """Mock plan generation for development."""
        
        prompt_lower = prompt.lower()
        
        if "inbox" in prompt_lower or "email" in prompt_lower:
            return {
                "intent": "scan inbox and process bills",
                "steps": [
                    {
                        "step_number": 1,
                        "tool": "ocr_tool",
                        "action": "scan inbox messages",
                        "params": {"source": "inbox"},
                        "requires_confirmation": False
                    },
                    {
                        "step_number": 2,
                        "tool": "bill_parser",
                        "action": "parse bills and extract due dates",
                        "params": {},
                        "requires_confirmation": False
                    },
                    {
                        "step_number": 3,
                        "tool": "task_store",
                        "action": "store tasks in database",
                        "params": {},
                        "requires_confirmation": False
                    },
                    {
                        "step_number": 4,
                        "tool": "calendar_tool",
                        "action": "create calendar reminders",
                        "params": {},
                        "requires_confirmation": True
                    },
                    {
                        "step_number": 5,
                        "tool": "notification_tool",
                        "action": "send notifications for upcoming due dates",
                        "params": {},
                        "requires_confirmation": False
                    }
                ]
            }
        
        elif "bill" in prompt_lower:
            return {
                "intent": "process bills and create reminders",
                "steps": [
                    {
                        "step_number": 1,
                        "tool": "bill_parser",
                        "action": "parse bill documents",
                        "params": {},
                        "requires_confirmation": False
                    },
                    {
                        "step_number": 2,
                        "tool": "task_store",
                        "action": "save bill tasks",
                        "params": {},
                        "requires_confirmation": False
                    },
                    {
                        "step_number": 3,
                        "tool": "notification_tool",
                        "action": "notify about due dates",
                        "params": {},
                        "requires_confirmation": False
                    }
                ]
            }
        
        return {
            "intent": "general task automation",
            "steps": [
                {
                    "step_number": 1,
                    "tool": "task_store",
                    "action": "create task from prompt",
                    "params": {"description": prompt},
                    "requires_confirmation": False
                }
            ]
        }
    
    def _mock_extract_entities(self, text: str, entity_types: list[str]) -> Dict[str, Any]:
        """Mock entity extraction for development."""
        
        entities = {}
        text_lower = text.lower()
        
        if "amount" in entity_types or "total" in entity_types:
            # Simple regex-like extraction
            import re
            amounts = re.findall(r'\$[\d,]+\.?\d*', text)
            if amounts:
                entities["amount"] = amounts[0]
        
        if "due_date" in entity_types or "date" in entity_types:
            # Look for date patterns
            import re
            date_patterns = re.findall(r'(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}', text_lower)
            if date_patterns:
                entities["due_date"] = date_patterns[0]
            else:
                # Fallback
                entities["due_date"] = (datetime.now() + timedelta(days=14)).strftime("%B %d, %Y")
        
        if "account_number" in entity_types:
            import re
            accounts = re.findall(r'[A-Z]{2}-\d{6}', text)
            if accounts:
                entities["account_number"] = accounts[0]
        
        return entities