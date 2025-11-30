"""Planning agent for generating execution plans."""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class Planner:
    """Agent responsible for planning task execution."""
    
    def __init__(self, gemini_client):
        self.gemini_client = gemini_client
    
    def create_plan(self, prompt: str) -> Dict[str, Any]:
        """Create an execution plan from a user prompt."""
        
        logger.info(f"Creating plan for: {prompt}")
        
        plan = self.gemini_client.generate_plan(prompt)
        
        # Validate plan structure
        if not self._validate_plan(plan):
            logger.warning("Plan validation failed, using simple fallback")
            plan = self._create_fallback_plan(prompt)
        
        logger.info(f"Plan created with {len(plan.get('steps', []))} steps")
        
        return plan
    
    def _validate_plan(self, plan: Dict[str, Any]) -> bool:
        """Validate that a plan has the required structure."""
        
        if not isinstance(plan, dict):
            return False
        
        if "intent" not in plan or "steps" not in plan:
            return False
        
        if not isinstance(plan["steps"], list):
            return False
        
        for step in plan["steps"]:
            if not isinstance(step, dict):
                return False
            
            required_keys = ["step_number", "tool", "action"]
            if not all(key in step for key in required_keys):
                return False
        
        return True
    
    def _create_fallback_plan(self, prompt: str) -> Dict[str, Any]:
        """Create a simple fallback plan."""
        
        return {
            "intent": prompt,
            "steps": [
                {
                    "step_number": 1,
                    "tool": "task_store",
                    "action": "Create task from prompt",
                    "params": {"description": prompt},
                    "requires_confirmation": False
                }
            ]
        }
    
    def optimize_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize an execution plan (future enhancement)."""
        
        # Could add logic to:
        # - Reorder steps for efficiency
        # - Combine similar operations
        # - Add error handling steps
        
        return plan