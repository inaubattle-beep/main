#!/usr/bin/env python3
"""
Agent Manager
Manages the lifecycle of agents including creation, monitoring, and termination.
Integrates with the God AGI Agent for dynamic agent management.
"""

import asyncio
import importlib.util
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import psutil
import threading

from core.logger import logger
from memory.database import AsyncSessionLocal
from memory.models import Agent, Task, TaskState
from core.task_manager import TaskManager
from core.llm import llm_client

class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    TERMINATED = "terminated"

class AgentType(Enum):
    SYSTEM = "system"
    USER = "user"
    TEMPORARY = "temporary"
    SPECIALIZED = "specialized"

@dataclass
class AgentInfo:
    """Information about an agent"""
    agent_id: str
    process_id: Optional[int]
    status: AgentStatus
    agent_type: AgentType
    created_at: datetime
    last_seen: datetime
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    tasks_completed: int = 0
    tasks_failed: int = 0
    error_count: int = 0
    parent_agent: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)

class AgentManager:
    """Manages agent lifecycle and operations"""
    
    def __init__(self):
        self.agents: Dict[str, AgentInfo] = {}
        self.agent_processes: Dict[str, subprocess.Popen] = {}
        self.agent_threads: Dict[str, threading.Thread] = {}
        self.is_running = False
        self.monitoring_task = None
        self.cleanup_task = None
        
        # Configuration
        self.max_agents = 100
        self.max_memory_per_agent = 1024  # MB
        self.max_cpu_per_agent = 50  # percentage
        self.monitoring_interval = 30  # seconds
        self.cleanup_interval = 3600  # 1 hour
        
    async def start(self):
        """Start the agent manager"""
        logger.info("Starting Agent Manager...")
        self.is_running = True
        
        # Start background tasks
        self.monitoring_task = asyncio.create_task(self._monitor_agents())
        self.cleanup_task = asyncio.create_task(self._cleanup_agents())
        
        # Load existing agents from database
        await self._load_agents_from_db()
        
        logger.info("Agent Manager started successfully")
    
    async def stop(self):
        """Stop the agent manager"""
        logger.info("Stopping Agent Manager...")
        self.is_running = False
        
        # Stop all agents
        for agent_id in list(self.agents.keys()):
            await self.terminate_agent(agent_id)
        
        # Stop background tasks
        if self.monitoring_task:
            self.monitoring_task.cancel()
        if self.cleanup_task:
            self.cleanup_task.cancel()
        
        logger.info("Agent Manager stopped")
    
    async def create_agent(self, agent_id: str, agent_type: AgentType = AgentType.USER, 
                          capabilities: List[str] = None, parent_agent: str = None) -> bool:
        """Create a new agent"""
        try:
            if len(self.agents) >= self.max_agents:
                logger.error(f"Maximum number of agents ({self.max_agents}) reached")
                return False
            
            if agent_id in self.agents:
                logger.warning(f"Agent {agent_id} already exists")
                return False
            
            # Create agent file if it doesn't exist
            agent_file = Path(f"agents/{agent_id}.py")
            if not agent_file.exists():
                await self._generate_agent_file(agent_id, agent_type, capabilities or [])
            
            # Register agent in database
            async with AsyncSessionLocal() as db:
                new_agent = Agent(
                    agent_id=agent_id,
                    username=agent_id,
                    hashed_password="auto_generated",
                    role=agent_type.value,
                    permissions={"execute": True, "create_agents": False}
                )
                db.add(new_agent)
                await db.commit()
            
            # Create agent info
            agent_info = AgentInfo(
                agent_id=agent_id,
                process_id=None,
                status=AgentStatus.IDLE,
                agent_type=agent_type,
                created_at=datetime.utcnow(),
                last_seen=datetime.utcnow(),
                parent_agent=parent_agent,
                capabilities=capabilities or []
            )
            
            self.agents[agent_id] = agent_info
            
            logger.info(f"Created agent: {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create agent {agent_id}: {e}")
            return False
    
    async def start_agent(self, agent_id: str) -> bool:
        """Start an agent"""
        try:
            if agent_id not in self.agents:
                logger.error(f"Agent {agent_id} not found")
                return False
            
            agent_info = self.agents[agent_id]
            if agent_info.status == AgentStatus.RUNNING:
                logger.warning(f"Agent {agent_id} is already running")
                return True
            
            # Start agent process
            agent_file = Path(f"agents/{agent_id}.py")
            if not agent_file.exists():
                logger.error(f"Agent file {agent_file} not found")
                return False
            
            # Use Python to run the agent
            process = subprocess.Popen([
                sys.executable, str(agent_file)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            agent_info.process_id = process.pid
            agent_info.status = AgentStatus.RUNNING
            agent_info.last_seen = datetime.utcnow()
            
            self.agent_processes[agent_id] = process
            
            logger.info(f"Started agent: {agent_id} (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start agent {agent_id}: {e}")
            return False
    
    async def stop_agent(self, agent_id: str) -> bool:
        """Stop an agent"""
        try:
            if agent_id not in self.agents:
                logger.error(f"Agent {agent_id} not found")
                return False
            
            agent_info = self.agents[agent_id]
            if agent_info.status != AgentStatus.RUNNING:
                logger.warning(f"Agent {agent_id} is not running")
                return True
            
            # Terminate process
            if agent_id in self.agent_processes:
                process = self.agent_processes[agent_id]
                try:
                    process.terminate()
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                finally:
                    del self.agent_processes[agent_id]
            
            agent_info.status = AgentStatus.IDLE
            agent_info.process_id = None
            
            logger.info(f"Stopped agent: {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop agent {agent_id}: {e}")
            return False
    
    async def terminate_agent(self, agent_id: str) -> bool:
        """Terminate an agent completely"""
        try:
            # Stop the agent first
            await self.stop_agent(agent_id)
            
            # Remove from tracking
            if agent_id in self.agents:
                del self.agents[agent_id]
            
            # Remove from database
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    "DELETE FROM agents WHERE agent_id = :agent_id",
                    {"agent_id": agent_id}
                )
                await db.commit()
            
            logger.info(f"Terminated agent: {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to terminate agent {agent_id}: {e}")
            return False
    
    async def get_agent_status(self, agent_id: str) -> Optional[AgentInfo]:
        """Get status of an agent"""
        return self.agents.get(agent_id)
    
    async def list_agents(self) -> List[AgentInfo]:
        """List all agents"""
        return list(self.agents.values())
    
    async def assign_task(self, agent_id: str, task_description: str) -> bool:
        """Assign a task to an agent"""
        try:
            if agent_id not in self.agents:
                logger.error(f"Agent {agent_id} not found")
                return False
            
            agent_info = self.agents[agent_id]
            if agent_info.status != AgentStatus.RUNNING:
                logger.warning(f"Agent {agent_id} is not running")
                return False
            
            # Create task in database
            async with AsyncSessionLocal() as db:
                new_task = Task(
                    agent_id=agent_id,
                    description=task_description,
                    state=TaskState.RUNNING
                )
                db.add(new_task)
                await db.commit()
            
            logger.info(f"Assigned task to agent {agent_id}: {task_description}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to assign task to agent {agent_id}: {e}")
            return False
    
    async def get_agent_performance(self, agent_id: str) -> Dict[str, Any]:
        """Get performance metrics for an agent"""
        try:
            if agent_id not in self.agents:
                return {"error": "Agent not found"}
            
            agent_info = self.agents[agent_id]
            
            # Get task statistics from database
            async with AsyncSessionLocal() as db:
                completed_tasks = await db.execute(
                    "SELECT COUNT(*) FROM tasks WHERE agent_id = :agent_id AND state = 'COMPLETED'",
                    {"agent_id": agent_id}
                )
                failed_tasks = await db.execute(
                    "SELECT COUNT(*) FROM tasks WHERE agent_id = :agent_id AND state = 'FAILED'",
                    {"agent_id": agent_id}
                )
                
                total_tasks = completed_tasks.scalar() + failed_tasks.scalar()
                success_rate = (completed_tasks.scalar() / total_tasks * 100) if total_tasks > 0 else 0
            
            return {
                "agent_id": agent_id,
                "status": agent_info.status.value,
                "agent_type": agent_info.agent_type.value,
                "created_at": agent_info.created_at.isoformat(),
                "last_seen": agent_info.last_seen.isoformat(),
                "memory_usage": agent_info.memory_usage,
                "cpu_usage": agent_info.cpu_usage,
                "tasks_completed": agent_info.tasks_completed,
                "tasks_failed": agent_info.tasks_failed,
                "error_count": agent_info.error_count,
                "total_tasks": total_tasks,
                "success_rate": success_rate,
                "capabilities": agent_info.capabilities
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance for agent {agent_id}: {e}")
            return {"error": str(e)}
    
    async def _generate_agent_file(self, agent_id: str, agent_type: AgentType, capabilities: List[str]):
        """Generate agent Python file"""
        capabilities_imports = ""
        if "web_scraping" in capabilities:
            capabilities_imports += "from bs4 import BeautifulSoup\nimport requests\n"
        if "data_analysis" in capabilities:
            capabilities_imports += "import pandas as pd\nimport numpy as np\n"
        if "ml_training" in capabilities:
            capabilities_imports += "from sklearn.model_selection import train_test_split\n"
        if "code_generation" in capabilities:
            capabilities_imports += "from core.llm import llm_client\n"
        
        agent_code = f'''#!/usr/bin/env python3
"""
Auto-generated Agent: {agent_id}
Type: {agent_type.value}
Capabilities: {', '.join(capabilities)}
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the main directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.base import BaseAgent
from core.logger import logger
{capabilities_imports}

class {agent_id.replace('-', '_').title().replace('_', '')}(BaseAgent):
    def __init__(self):
        super().__init__("{agent_id}")
        self.agent_type = "{agent_type.value}"
        self.capabilities = {capabilities}
        self.is_running = False
    
    async def process(self):
        """Main processing logic for this agent"""
        if not self.is_running:
            self.is_running = True
            logger.info(f"Agent {self.agent_id} started processing")
        
        try:
            # Agent-specific logic would go here
            # This is where the agent would perform its specialized tasks
            logger.debug(f"Agent {self.agent_id} processing with capabilities: {self.capabilities}")
            
            # Example: Perform capability-specific tasks
            if "code_generation" in self.capabilities:
                await self._generate_code()
            elif "data_analysis" in self.capabilities:
                await self._analyze_data()
            elif "web_scraping" in self.capabilities:
                await self._scrape_web()
            
            await asyncio.sleep(1)  # Prevent busy waiting
            
        except Exception as e:
            logger.error(f"Agent {self.agent_id} error: {e}")
            raise
    
    async def _generate_code(self):
        """Example code generation task"""
        logger.info(f"Agent {self.agent_id} generating code...")
        # Implementation would use LLM to generate code
    
    async def _analyze_data(self):
        """Example data analysis task"""
        logger.info(f"Agent {self.agent_id} analyzing data...")
        # Implementation would analyze data using pandas/numpy
    
    async def _scrape_web(self):
        """Example web scraping task"""
        logger.info(f"Agent {self.agent_id} scraping web...")
        # Implementation would scrape websites using requests/BeautifulSoup
    
    def stop(self):
        """Stop the agent"""
        self.is_running = False
        logger.info(f"Agent {self.agent_id} stopped")

if __name__ == "__main__":
    agent = {agent_id.replace('-', '_').title().replace('_', '')}()
    try:
        asyncio.run(agent.run())
    except KeyboardInterrupt:
        logger.info("Agent interrupted by user")
        agent.stop()
    except Exception as e:
        logger.error(f"Agent {agent_id} failed: {e}")
        agent.stop()
'''
        
        agent_file = Path(f"agents/{agent_id}.py")
        with open(agent_file, 'w') as f:
            f.write(agent_code)
        
        logger.info(f"Generated agent file: {agent_file}")
    
    async def _load_agents_from_db(self):
        """Load existing agents from database"""
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute("SELECT * FROM agents")
                db_agents = result.fetchall()
                
                for db_agent in db_agents:
                    agent_info = AgentInfo(
                        agent_id=db_agent.agent_id,
                        process_id=None,
                        status=AgentStatus.IDLE,
                        agent_type=AgentType(db_agent.role),
                        created_at=db_agent.created_at or datetime.utcnow(),
                        last_seen=datetime.utcnow(),
                        capabilities=[]
                    )
                    self.agents[db_agent.agent_id] = agent_info
                
                logger.info(f"Loaded {len(self.agents)} agents from database")
                
        except Exception as e:
            logger.error(f"Failed to load agents from database: {e}")
    
    async def _monitor_agents(self):
        """Monitor agent health and performance"""
        while self.is_running:
            try:
                current_time = datetime.utcnow()
                
                for agent_id, agent_info in self.agents.items():
                    # Check if process is still running
                    if agent_info.process_id:
                        try:
                            process = psutil.Process(agent_info.process_id)
                            if not process.is_running():
                                agent_info.status = AgentStatus.ERROR
                                agent_info.error_count += 1
                                logger.warning(f"Agent {agent_id} process died")
                            else:
                                # Update resource usage
                                agent_info.memory_usage = process.memory_info().rss / 1024 / 1024  # MB
                                agent_info.cpu_usage = process.cpu_percent()
                                agent_info.last_seen = current_time
                                
                                # Check resource limits
                                if agent_info.memory_usage > self.max_memory_per_agent:
                                    logger.warning(f"Agent {agent_id} exceeded memory limit: {agent_info.memory_usage}MB")
                                    await self.stop_agent(agent_id)
                                
                                if agent_info.cpu_usage > self.max_cpu_per_agent:
                                    logger.warning(f"Agent {agent_id} exceeded CPU limit: {agent_info.cpu_usage}%")
                                    await self.stop_agent(agent_id)
                        
                        except psutil.NoSuchProcess:
                            agent_info.status = AgentStatus.ERROR
                            agent_info.error_count += 1
                            logger.warning(f"Agent {agent_id} process not found")
                    
                    # Check for stale agents (no activity for too long)
                    if current_time - agent_info.last_seen > timedelta(hours=1):
                        if agent_info.status == AgentStatus.RUNNING:
                            logger.warning(f"Agent {agent_id} appears stale, restarting...")
                            await self.stop_agent(agent_id)
                            await self.start_agent(agent_id)
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Agent monitoring error: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _cleanup_agents(self):
        """Clean up terminated and error agents"""
        while self.is_running:
            try:
                current_time = datetime.utcnow()
                agents_to_remove = []
                
                for agent_id, agent_info in self.agents.items():
                    # Remove agents with too many errors
                    if agent_info.error_count > 5:
                        logger.warning(f"Removing agent {agent_id} due to too many errors: {agent_info.error_count}")
                        agents_to_remove.append(agent_id)
                    
                    # Remove stale agents that haven't been seen in 24 hours
                    if current_time - agent_info.last_seen > timedelta(hours=24):
                        if agent_info.status in [AgentStatus.ERROR, AgentStatus.IDLE]:
                            logger.info(f"Removing stale agent {agent_id}")
                            agents_to_remove.append(agent_id)
                
                # Remove agents
                for agent_id in agents_to_remove:
                    await self.terminate_agent(agent_id)
                
                await asyncio.sleep(self.cleanup_interval)
                
            except Exception as e:
                logger.error(f"Agent cleanup error: {e}")
                await asyncio.sleep(60)

# Global agent manager instance
agent_manager = AgentManager()

# Convenience functions for external use
async def create_agent(agent_id: str, agent_type: AgentType = AgentType.USER, 
                      capabilities: List[str] = None, parent_agent: str = None) -> bool:
    """Create a new agent"""
    return await agent_manager.create_agent(agent_id, agent_type, capabilities, parent_agent)

async def start_agent(agent_id: str) -> bool:
    """Start an agent"""
    return await agent_manager.start_agent(agent_id)

async def stop_agent(agent_id: str) -> bool:
    """Stop an agent"""
    return await agent_manager.stop_agent(agent_id)

async def terminate_agent(agent_id: str) -> bool:
    """Terminate an agent completely"""
    return await agent_manager.terminate_agent(agent_id)

async def get_agent_status(agent_id: str) -> Optional[AgentInfo]:
    """Get status of an agent"""
    return await agent_manager.get_agent_status(agent_id)

async def list_agents() -> List[AgentInfo]:
    """List all agents"""
    return await agent_manager.list_agents()

async def assign_task(agent_id: str, task_description: str) -> bool:
    """Assign a task to an agent"""
    return await agent_manager.assign_task(agent_id, task_description)

async def get_agent_performance(agent_id: str) -> Dict[str, Any]:
    """Get performance metrics for an agent"""
    return await agent_manager.get_agent_performance(agent_id)