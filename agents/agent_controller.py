"""Main agent controller for orchestrating tool execution."""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class AgentController:
    """Controller for orchestrating agent execution."""
    
    def __init__(self, planner, tools: List[Any]):
        self.planner = planner
        self.tools = {tool.name: tool for tool in tools}
        self.execution_history: List[Dict[str, Any]] = []
    
    def execute_prompt(self, prompt: str, auto_confirm: bool = False) -> Dict[str, Any]:
        """Execute a user prompt end-to-end."""
        
        logger.info(f"Executing prompt: {prompt}")
        
        # Step 1: Create plan
        plan = self.planner.create_plan(prompt)
        print(f"\n📋 Plan created: {plan['intent']}")
        print(f"   Steps: {len(plan['steps'])}\n")
        
        # Step 2: Execute each step
        results = []
        shared_context = {}
        
        for step in plan["steps"]:
            step_num = step.get("step_number", 0)
            tool_name = step.get("tool")
            action = step.get("action")
            params = step.get("params", {})
            requires_confirmation = step.get("requires_confirmation", False)
            
            print(f"Step {step_num}: {action} (using {tool_name})")
            
            # Get the tool
            tool = self.tools.get(tool_name)
            if not tool:
                logger.warning(f"Tool not found: {tool_name}")
                results.append({
                    "step": step_num,
                    "status": "skipped",
                    "reason": f"Tool not found: {tool_name}"
                })
                continue
            
            # Merge shared context into params
            params.update(shared_context)
            
            # Dry run
            dry_run_result = tool.dry_run(params)
            print(f"   Dry run: {dry_run_result.get('action')}")
            
            # Confirmation if needed
            if requires_confirmation and not auto_confirm:
                confirm = self._request_confirmation(step, dry_run_result)
                if not confirm:
                    print(f"   ❌ Skipped by user\n")
                    results.append({
                        "step": step_num,
                        "status": "skipped",
                        "reason": "User declined"
                    })
                    continue
            
            # Execute
            try:
                result = tool.execute(params)
                print(f"   ✅ Completed\n")
                
                results.append({
                    "step": step_num,
                    "status": "success",
                    "result": result
                })
                
                # Update shared context with results
                self._update_shared_context(shared_context, tool_name, result)
                
            except Exception as e:
                logger.error(f"Step {step_num} failed: {e}")
                print(f"   ❌ Failed: {e}\n")
                
                results.append({
                    "step": step_num,
                    "status": "failed",
                    "error": str(e)
                })
        
        # Save execution history
        execution = {
            "prompt": prompt,
            "plan": plan,
            "results": results
        }
        self.execution_history.append(execution)
        
        return execution
    
    def _request_confirmation(self, step: Dict[str, Any], dry_run: Dict[str, Any]) -> bool:
        """Request user confirmation for a step."""
        
        print(f"\n⚠️  Confirmation required:")
        print(f"   Action: {step.get('action')}")
        print(f"   Details: {dry_run.get('action')}")
        
        response = input("   Proceed? (y/n): ").strip().lower()
        return response == 'y'
    
    def _update_shared_context(self, context: Dict[str, Any], tool_name: str, result: Dict[str, Any]) -> None:
        """Update shared context with tool results."""
        
        # Extract useful data for next steps
        if tool_name == "ocr_tool":
            context["items"] = result.get("items", [])
        
        elif tool_name == "bill_parser":
            context["bills"] = result.get("bills", [])
        
        elif tool_name == "task_store":
            context["tasks"] = result.get("tasks", [])
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get execution history."""
        return self.execution_history