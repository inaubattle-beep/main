#!/usr/bin/env python3
"""
Advanced Task Planner and Execution System
Handles complex task planning, execution, and management for the God AGI Agent.
"""

import asyncio
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Union
from concurrent.futures import ThreadPoolExecutor
import traceback

from core.llm import llm_client
from core.logger import logger
from memory.database import AsyncSessionLocal
from memory.models import Task, TaskState, Agent
from agents.agent_manager import agent_manager

class TaskType(Enum):
    SIMPLE = "simple"
    COMPLEX = "complex"
    RECURSIVE = "recursive"
    COLLABORATIVE = "collaborative"
    CRITICAL = "critical"

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

@dataclass
class TaskPlan:
    """A planned task with all its details"""
    task_id: str
    description: str
    task_type: TaskType
    priority: int  # 1-10, higher is more important
    estimated_duration: int  # in seconds
    required_capabilities: List[str]
    dependencies: List[str] = field(default_factory=list)
    max_retries: int = 3
    timeout: int = 3600  # 1 hour default
    assigned_agent: Optional[str] = None
    subtasks: List['TaskPlan'] = field(default_factory=list)
    execution_order: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[str] = None
    error: Optional[str] = None
    retry_count: int = 0

class TaskExecutor(ABC):
    """Abstract base class for task executors"""
    
    @abstractmethod
    async def execute(self, task: TaskPlan) -> Dict[str, Any]:
        """Execute a task and return result"""
        pass

class SimpleTaskExecutor(TaskExecutor):
    """Executor for simple, atomic tasks"""
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    async def execute(self, task: TaskPlan) -> Dict[str, Any]:
        """Execute a simple task using LLM"""
        try:
            start_time = time.time()
            
            # Use LLM to execute the task
            prompt = f"""
            Execute this task: {task.description}
            
            Provide a detailed response with:
            1. Execution steps taken
            2. Result of execution
            3. Any issues encountered
            4. Suggestions for improvement
            
            Return as JSON with keys: steps, result, issues, suggestions
            """
            
            response = await self.llm.generate_response(prompt)
            result_data = json.loads(response)
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "execution_time": execution_time,
                "result": result_data,
                "task_id": task.task_id
            }
            
        except Exception as e:
            logger.error(f"Simple task execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "task_id": task.task_id
            }

class ComplexTaskExecutor(TaskExecutor):
    """Executor for complex, multi-step tasks"""
    
    def __init__(self, task_planner):
        self.task_planner = task_planner
    
    async def execute(self, task: TaskPlan) -> Dict[str, Any]:
        """Execute a complex task by breaking it down into subtasks"""
        try:
            start_time = time.time()
            
            # Plan subtasks if not already planned
            if not task.subtasks:
                task.subtasks = await self.task_planner.plan_subtasks(task)
            
            # Execute subtasks in order
            results = []
            for subtask in sorted(task.subtasks, key=lambda x: x.execution_order):
                result = await self.task_planner.execute_task(subtask)
                results.append(result)
                
                # Check if task should continue based on dependencies
                if not result.get("success", False) and subtask.task_id in task.dependencies:
                    return {
                        "success": False,
                        "error": f"Subtask {subtask.task_id} failed, blocking main task",
                        "task_id": task.task_id,
                        "results": results
                    }
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "execution_time": execution_time,
                "results": results,
                "task_id": task.task_id
            }
            
        except Exception as e:
            logger.error(f"Complex task execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "task_id": task.task_id
            }

class CollaborativeTaskExecutor(TaskExecutor):
    """Executor for tasks requiring multiple agents"""
    
    def __init__(self, agent_manager):
        self.agent_manager = agent_manager
    
    async def execute(self, task: TaskPlan) -> Dict[str, Any]:
        """Execute a task using multiple specialized agents"""
        try:
            start_time = time.time()
            
            # Find suitable agents for this task
            suitable_agents = await self._find_suitable_agents(task.required_capabilities)
            
            if not suitable_agents:
                # Create specialized agents if none exist
                suitable_agents = await self._create_specialized_agents(task)
            
            # Assign subtasks to agents
            subtasks = await self._distribute_task(task, suitable_agents)
            results = []
            
            # Execute subtasks concurrently
            tasks = []
            for agent_id, subtask in subtasks.items():
                tasks.append(self._execute_subtask_with_agent(agent_id, subtask))
            
            subtask_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(subtask_results):
                if isinstance(result, Exception):
                    results.append({
                        "agent_id": list(subtasks.keys())[i],
                        "success": False,
                        "error": str(result)
                    })
                else:
                    results.append(result)
            
            execution_time = time.time() - start_time
            
            # Check if all subtasks succeeded
            all_succeeded = all(r.get("success", False) for r in results)
            
            return {
                "success": all_succeeded,
                "execution_time": execution_time,
                "results": results,
                "task_id": task.task_id,
                "agents_used": list(subtasks.keys())
            }
            
        except Exception as e:
            logger.error(f"Collaborative task execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "task_id": task.task_id
            }
    
    async def _find_suitable_agents(self, capabilities: List[str]) -> List[str]:
        """Find agents with required capabilities"""
        agents = await agent_manager.list_agents()
        suitable = []
        
        for agent in agents:
            if all(cap in agent.capabilities for cap in capabilities):
                suitable.append(agent.agent_id)
        
        return suitable
    
    async def _create_specialized_agents(self, task: TaskPlan) -> List[str]:
        """Create specialized agents for the task"""
        from agents.agent_manager import create_agent, AgentType
        
        agent_ids = []
        for i, capability in enumerate(task.required_capabilities):
            agent_id = f"{task.task_id}_agent_{i}_{int(time.time())}"
            success = await create_agent(
                agent_id=agent_id,
                agent_type=AgentType.SPECIALIZED,
                capabilities=[capability]
            )
            if success:
                agent_ids.append(agent_id)
        
        return agent_ids
    
    async def _distribute_task(self, task: TaskPlan, agents: List[str]) -> Dict[str, TaskPlan]:
        """Distribute task among agents"""
        # Simple round-robin distribution for now
        subtasks = {}
        for i, agent_id in enumerate(agents):
            subtask = TaskPlan(
                task_id=f"{task.task_id}_subtask_{i}",
                description=f"Part of {task.description} handled by {agent_id}",
                task_type=TaskType.SIMPLE,
                priority=task.priority,
                estimated_duration=task.estimated_duration // len(agents),
                required_capabilities=task.required_capabilities,
                assigned_agent=agent_id
            )
            subtasks[agent_id] = subtask
        
        return subtasks
    
    async def _execute_subtask_with_agent(self, agent_id: str, subtask: TaskPlan) -> Dict[str, Any]:
        """Execute a subtask with a specific agent"""
        try:
            # Start agent if not running
            await agent_manager.start_agent(agent_id)
            
            # Assign task to agent
            success = await agent_manager.assign_task(agent_id, subtask.description)
            
            if not success:
                return {
                    "agent_id": agent_id,
                    "success": False,
                    "error": "Failed to assign task to agent"
                }
            
            # Wait for task completion (simplified for now)
            await asyncio.sleep(subtask.estimated_duration)
            
            # Get agent performance
            performance = await agent_manager.get_agent_performance(agent_id)
            
            return {
                "agent_id": agent_id,
                "success": True,
                "performance": performance,
                "subtask_id": subtask.task_id
            }
            
        except Exception as e:
            return {
                "agent_id": agent_id,
                "success": False,
                "error": str(e),
                "subtask_id": subtask.task_id
            }

class TaskPlanner:
    """Main task planning and execution system"""
    
    def __init__(self):
        self.llm = llm_client
        self.agent_manager = agent_manager
        self.is_running = False
        
        # Executors for different task types
        self.executors = {
            TaskType.SIMPLE: SimpleTaskExecutor(self.llm),
            TaskType.COMPLEX: ComplexTaskExecutor(self),
            TaskType.COLLABORATIVE: CollaborativeTaskExecutor(self.agent_manager),
            TaskType.CRITICAL: SimpleTaskExecutor(self.llm),  # Critical tasks use direct LLM
        }
        
        # Task tracking
        self.active_tasks: Dict[str, TaskPlan] = {}
        self.completed_tasks: List[TaskPlan] = []
        self.failed_tasks: List[TaskPlan] = []
        
        # Configuration
        self.max_concurrent_tasks = 10
        self.task_timeout = 3600  # 1 hour
        self.retry_delay = 60  # 1 minute
    
    async def start(self):
        """Start the task planner"""
        logger.info("Starting Task Planner...")
        self.is_running = True
        logger.info("Task Planner started successfully")
    
    async def stop(self):
        """Stop the task planner"""
        logger.info("Stopping Task Planner...")
        self.is_running = False
        logger.info("Task Planner stopped")
    
    async def plan_task(self, description: str, priority: int = 5, 
                       capabilities: List[str] = None) -> TaskPlan:
        """Plan a new task"""
        try:
            # Determine task type and complexity
            task_type = await self._determine_task_type(description, capabilities or [])
            
            # Estimate duration
            estimated_duration = await self._estimate_duration(description, task_type)
            
            # Determine required capabilities
            required_capabilities = capabilities or await self._extract_capabilities(description)
            
            # Create task plan
            task = TaskPlan(
                task_id=f"task_{int(time.time())}_{hash(description) % 10000}",
                description=description,
                task_type=task_type,
                priority=priority,
                estimated_duration=estimated_duration,
                required_capabilities=required_capabilities
            )
            
            # Plan subtasks for complex tasks
            if task_type == TaskType.COMPLEX:
                task.subtasks = await self._plan_subtasks(task)
            
            logger.info(f"Planned task: {task.task_id} - {description}")
            return task
            
        except Exception as e:
            logger.error(f"Task planning failed: {e}")
            raise
    
    async def execute_task(self, task: TaskPlan) -> Dict[str, Any]:
        """Execute a planned task"""
        try:
            if not self.is_running:
                return {"success": False, "error": "Task planner not running"}
            
            # Check if task can be executed
            if len(self.active_tasks) >= self.max_concurrent_tasks:
                return {"success": False, "error": "Maximum concurrent tasks reached"}
            
            # Start task execution
            task.started_at = datetime.utcnow()
            self.active_tasks[task.task_id] = task
            
            # Get appropriate executor
            executor = self.executors.get(task.task_type)
            if not executor:
                return {"success": False, "error": f"No executor for task type: {task.task_type}"}
            
            # Execute task with timeout
            try:
                result = await asyncio.wait_for(
                    executor.execute(task),
                    timeout=task.timeout
                )
            except asyncio.TimeoutError:
                result = {
                    "success": False,
                    "error": "Task execution timed out",
                    "task_id": task.task_id
                }
            
            # Update task status
            task.completed_at = datetime.utcnow()
            task.result = result.get("result") if result.get("success") else None
            task.error = result.get("error") if not result.get("success") else None
            
            # Move to appropriate list
            del self.active_tasks[task.task_id]
            if result.get("success"):
                self.completed_tasks.append(task)
                logger.info(f"Task completed: {task.task_id}")
            else:
                self.failed_tasks.append(task)
                logger.error(f"Task failed: {task.task_id} - {task.error}")
            
            return result
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return {"success": False, "error": str(e), "task_id": task.task_id}
    
    async def execute_task_with_retry(self, task: TaskPlan) -> Dict[str, Any]:
        """Execute a task with retry logic"""
        for attempt in range(task.max_retries):
            result = await self.execute_task(task)
            
            if result.get("success"):
                return result
            
            # Increment retry count
            task.retry_count += 1
            
            if attempt < task.max_retries - 1:
                logger.warning(f"Task {task.task_id} failed on attempt {attempt + 1}, retrying...")
                await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
        
        logger.error(f"Task {task.task_id} failed after {task.max_retries} attempts")
        return result
    
    async def plan_and_execute(self, description: str, priority: int = 5, 
                             capabilities: List[str] = None, execute: bool = True) -> Dict[str, Any]:
        """Plan and execute a task in one operation"""
        try:
            # Plan the task
            task = await self.plan_task(description, priority, capabilities)
            
            if not execute:
                return {
                    "success": True,
                    "task_id": task.task_id,
                    "plan": {
                        "description": task.description,
                        "type": task.task_type.value,
                        "priority": task.priority,
                        "estimated_duration": task.estimated_duration,
                        "capabilities": task.required_capabilities,
                        "subtasks": [st.task_id for st in task.subtasks]
                    }
                }
            
            # Execute the task
            result = await self.execute_task_with_retry(task)
            return result
            
        except Exception as e:
            logger.error(f"Plan and execute failed: {e}")
            return {"success": False, "error": str(e)}
    
    # Helper methods
    
    async def _determine_task_type(self, description: str, capabilities: List[str]) -> TaskType:
        """Determine the type of task based on description and capabilities"""
        description_lower = description.lower()
        
        # Check for complex task indicators
        complex_indicators = [
            "multiple steps", "break down", "analyze", "plan", "design", "implement"
        ]
        
        # Check for collaborative task indicators
        collaborative_indicators = [
            "team", "multiple agents", "collaborate", "coordinate", "distributed"
        ]
        
        # Check for critical task indicators
        critical_indicators = [
            "urgent", "critical", "emergency", "immediate", "time-sensitive"
        ]
        
        if any(indicator in description_lower for indicator in critical_indicators):
            return TaskType.CRITICAL
        elif any(indicator in description_lower for indicator in collaborative_indicators):
            return TaskType.COLLABORATIVE
        elif any(indicator in description_lower for indicator in complex_indicators):
            return TaskType.COMPLEX
        else:
            return TaskType.SIMPLE
    
    async def _estimate_duration(self, description: str, task_type: TaskType) -> int:
        """Estimate task duration in seconds"""
        base_duration = 300  # 5 minutes default
        
        if task_type == TaskType.SIMPLE:
            return base_duration
        elif task_type == TaskType.COMPLEX:
            return base_duration * 4  # 20 minutes
        elif task_type == TaskType.COLLABORATIVE:
            return base_duration * 2  # 10 minutes
        elif task_type == TaskType.CRITICAL:
            return base_duration // 2  # 2.5 minutes
        
        return base_duration
    
    async def _extract_capabilities(self, description: str) -> List[str]:
        """Extract required capabilities from task description"""
        prompt = f"""
        Extract the required capabilities for this task:
        
        Task: {description}
        
        Return a JSON array of capabilities needed. Common capabilities include:
        - code_generation
        - data_analysis
        - web_scraping
        - ml_training
        - optimization
        - testing
        - deployment
        - security_analysis
        - performance_monitoring
        - database_management
        - api_integration
        - cloud_operations
        - devops
        - ui_ux_design
        - game_development
        - scientific_computing
        - natural_language_processing
        - computer_vision
        - robotics
        - iot_integration
        
        Return only the JSON array.
        """
        
        try:
            response = await self.llm.generate_response(prompt)
            capabilities = json.loads(response)
            return capabilities if isinstance(capabilities, list) else []
        except:
            return ["general_purpose"]
    
    async def _plan_subtasks(self, task: TaskPlan) -> List[TaskPlan]:
        """Plan subtasks for a complex task"""
        prompt = f"""
        Break down this complex task into subtasks:
        
        Task: {task.description}
        Required Capabilities: {', '.join(task.required_capabilities)}
        
        For each subtask, provide:
        - task_id (unique identifier)
        - description
        - priority (1-10)
        - estimated_duration (in seconds)
        - required_capabilities
        - dependencies (other subtask IDs)
        - execution_order (0-based index)
        
        Return as JSON array of subtask specifications.
        """
        
        try:
            response = await self.llm.generate_response(prompt)
            subtask_data = json.loads(response)
            
            subtasks = []
            for data in subtask_data:
                subtask = TaskPlan(
                    task_id=data.get("task_id", f"{task.task_id}_subtask_{len(subtasks)}"),
                    description=data.get("description", ""),
                    task_type=TaskType.SIMPLE,
                    priority=data.get("priority", 5),
                    estimated_duration=data.get("estimated_duration", 300),
                    required_capabilities=data.get("required_capabilities", []),
                    dependencies=data.get("dependencies", []),
                    execution_order=data.get("execution_order", 0),
                    assigned_agent=data.get("assigned_agent")
                )
                subtasks.append(subtask)
            
            return sorted(subtasks, key=lambda x: x.execution_order)
            
        except Exception as e:
            logger.error(f"Subtask planning failed: {e}")
            return []
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return {
                "task_id": task.task_id,
                "status": "running",
                "description": task.description,
                "type": task.task_type.value,
                "priority": task.priority,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "estimated_completion": (task.started_at + timedelta(seconds=task.estimated_duration)).isoformat() if task.started_at else None,
                "progress": 0.5  # Simplified progress calculation
            }
        
        # Check completed tasks
        for task in self.completed_tasks:
            if task.task_id == task_id:
                return {
                    "task_id": task.task_id,
                    "status": "completed",
                    "description": task.description,
                    "type": task.task_type.value,
                    "priority": task.priority,
                    "started_at": task.started_at.isoformat() if task.started_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "result": task.result
                }
        
        # Check failed tasks
        for task in self.failed_tasks:
            if task.task_id == task_id:
                return {
                    "task_id": task.task_id,
                    "status": "failed",
                    "description": task.description,
                    "type": task.task_type.value,
                    "priority": task.priority,
                    "started_at": task.started_at.isoformat() if task.started_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "error": task.error,
                    "retry_count": task.retry_count
                }
        
        return None
    
    async def get_active_tasks(self) -> List[Dict[str, Any]]:
        """Get all active tasks"""
        tasks = []
        for task in self.active_tasks.values():
            tasks.append({
                "task_id": task.task_id,
                "description": task.description,
                "type": task.task_type.value,
                "priority": task.priority,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "estimated_duration": task.estimated_duration,
                "progress": 0.5
            })
        return tasks
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.completed_at = datetime.utcnow()
            task.error = "Task cancelled by user"
            
            del self.active_tasks[task_id]
            self.failed_tasks.append(task)
            
            logger.info(f"Cancelled task: {task_id}")
            return True
        
        return False

# Global task planner instance
task_planner = TaskPlanner()

# Convenience functions for external use
async def plan_task(description: str, priority: int = 5, capabilities: List[str] = None) -> TaskPlan:
    """Plan a new task"""
    return await task_planner.plan_task(description, priority, capabilities)

async def execute_task(task: TaskPlan) -> Dict[str, Any]:
    """Execute a planned task"""
    return await task_planner.execute_task(task)

async def plan_and_execute(description: str, priority: int = 5, 
                         capabilities: List[str] = None, execute: bool = True) -> Dict[str, Any]:
    """Plan and execute a task in one operation"""
    return await task_planner.plan_and_execute(description, priority, capabilities, execute)

async def get_task_status(task_id: str) -> Optional[Dict[str, Any]]:
    """Get status of a specific task"""
    return await task_planner.get_task_status(task_id)

async def get_active_tasks() -> List[Dict[str, Any]]:
    """Get all active tasks"""
    return await task_planner.get_active_tasks()

async def cancel_task(task_id: str) -> bool:
    """Cancel a running task"""
    return await task_planner.cancel_task(task_id)