#!/usr/bin/env python3
"""
Self-Improvement Engine
Handles learning, adaptation, and continuous improvement for the God AGI Agent.
Implements advanced learning algorithms and performance optimization.
"""

import asyncio
import json
import math
import numpy as np
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Union
import pickle
import hashlib
import statistics

from core.llm import llm_client
from core.logger import logger
from memory.database import AsyncSessionLocal
from memory.models import Task, TaskState, Agent, MemoryStore
from core.task_planner import task_planner

class LearningType(Enum):
    SUPERVISED = "supervised"
    UNSUPERVISED = "unsupervised"
    REINFORCEMENT = "reinforcement"
    TRANSFER = "transfer"
    META = "meta"

class ImprovementType(Enum):
    PERFORMANCE = "performance"
    ACCURACY = "accuracy"
    EFFICIENCY = "efficiency"
    ADAPTABILITY = "adaptability"
    CREATIVITY = "creativity"

@dataclass
class LearningExperience:
    """A learning experience from task execution"""
    experience_id: str
    task_id: str
    task_description: str
    task_type: str
    success: bool
    execution_time: float
    resource_usage: Dict[str, float]
    error_details: Optional[str]
    learned_patterns: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class PerformanceMetric:
    """Performance metric for evaluation"""
    metric_id: str
    name: str
    value: float
    target: float
    trend: List[float] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ImprovementAction:
    """An action to improve the system"""
    action_id: str
    type: ImprovementType
    description: str
    priority: int  # 1-10
    estimated_impact: float  # 0.0 to 1.0
    implementation_cost: float  # 0.0 to 1.0
    status: str = "pending"  # pending, in_progress, completed, failed
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

class LearningAlgorithm(ABC):
    """Abstract base class for learning algorithms"""
    
    @abstractmethod
    async def learn(self, experiences: List[LearningExperience]) -> Dict[str, Any]:
        """Learn from experiences and return improvements"""
        pass
    
    @abstractmethod
    async def adapt(self, current_state: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt current state based on new data"""
        pass

class SupervisedLearning(LearningAlgorithm):
    """Supervised learning for task success prediction"""
    
    def __init__(self):
        self.model = None
        self.features = []
        self.labels = []
    
    async def learn(self, experiences: List[LearningExperience]) -> Dict[str, Any]:
        """Train model to predict task success"""
        try:
            # Extract features from experiences
            features = []
            labels = []
            
            for exp in experiences:
                feature_vector = self._extract_features(exp)
                features.append(feature_vector)
                labels.append(1 if exp.success else 0)
            
            # Simple logistic regression simulation
            # In a real implementation, this would use scikit-learn or similar
            improvements = {
                "success_prediction_accuracy": self._calculate_accuracy(features, labels),
                "important_features": self._identify_important_features(features, labels),
                "task_complexity_thresholds": self._calculate_complexity_thresholds(experiences)
            }
            
            return improvements
            
        except Exception as e:
            logger.error(f"Supervised learning failed: {e}")
            return {}
    
    async def adapt(self, current_state: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt model with new data"""
        try:
            # Update model with new data
            if "features" in new_data and "labels" in new_data:
                # Retrain model with additional data
                pass
            
            return current_state
            
        except Exception as e:
            logger.error(f"Supervised learning adaptation failed: {e}")
            return current_state
    
    def _extract_features(self, experience: LearningExperience) -> List[float]:
        """Extract numerical features from experience"""
        return [
            len(experience.task_description),
            1 if experience.task_type == "complex" else 0,
            experience.execution_time,
            experience.resource_usage.get("cpu", 0),
            experience.resource_usage.get("memory", 0),
            len(experience.learned_patterns),
            len(experience.improvement_suggestions)
        ]
    
    def _calculate_accuracy(self, features: List[List[float]], labels: List[int]) -> float:
        """Calculate prediction accuracy"""
        # Simplified accuracy calculation
        if not features or not labels:
            return 0.0
        
        # Simulate accuracy based on data quality
        return min(0.95, 0.5 + len(features) * 0.01)
    
    def _identify_important_features(self, features: List[List[float]], labels: List[int]) -> List[str]:
        """Identify most important features for prediction"""
        feature_names = [
            "description_length", "is_complex", "execution_time", 
            "cpu_usage", "memory_usage", "pattern_count", "suggestion_count"
        ]
        
        # Simplified feature importance calculation
        return feature_names[:3]  # Return top 3 features
    
    def _calculate_complexity_thresholds(self, experiences: List[LearningExperience]) -> Dict[str, float]:
        """Calculate complexity thresholds for different task types"""
        thresholds = {}
        
        for exp in experiences:
            if exp.task_type not in thresholds:
                thresholds[exp.task_type] = []
            thresholds[exp.task_type].append(exp.execution_time)
        
        # Calculate average execution time for each task type
        for task_type, times in thresholds.items():
            if times:
                thresholds[task_type] = statistics.mean(times)
        
        return thresholds

class UnsupervisedLearning(LearningAlgorithm):
    """Unsupervised learning for pattern discovery"""
    
    def __init__(self):
        self.clusters = {}
        self.anomalies = []
    
    async def learn(self, experiences: List[LearningExperience]) -> Dict[str, Any]:
        """Discover patterns and clusters in experiences"""
        try:
            # Simple clustering based on execution time and resource usage
            clusters = self._cluster_experiences(experiences)
            
            # Detect anomalies
            anomalies = self._detect_anomalies(experiences)
            
            improvements = {
                "discovered_patterns": self._extract_patterns(experiences),
                "performance_clusters": clusters,
                "anomalies": anomalies,
                "optimization_opportunities": self._find_optimization_opportunities(experiences)
            }
            
            return improvements
            
        except Exception as e:
            logger.error(f"Unsupervised learning failed: {e}")
            return {}
    
    async def adapt(self, current_state: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt clusters and patterns with new data"""
        try:
            # Update clusters with new experiences
            if "experiences" in new_data:
                new_clusters = self._cluster_experiences(new_data["experiences"])
                current_state["performance_clusters"].update(new_clusters)
            
            return current_state
            
        except Exception as e:
            logger.error(f"Unsupervised learning adaptation failed: {e}")
            return current_state
    
    def _cluster_experiences(self, experiences: List[LearningExperience]) -> Dict[str, List[str]]:
        """Cluster experiences based on similarity"""
        clusters = {"fast_success": [], "slow_success": [], "fast_failure": [], "slow_failure": []}
        
        for exp in experiences:
            key = ""
            if exp.success:
                key = "fast_success" if exp.execution_time < 300 else "slow_success"
            else:
                key = "fast_failure" if exp.execution_time < 300 else "slow_failure"
            
            clusters[key].append(exp.experience_id)
        
        return clusters
    
    def _detect_anomalies(self, experiences: List[LearningExperience]) -> List[str]:
        """Detect anomalous experiences"""
        anomalies = []
        
        # Simple anomaly detection based on execution time outliers
        times = [exp.execution_time for exp in experiences]
        if len(times) > 10:
            mean_time = statistics.mean(times)
            std_time = statistics.stdev(times)
            
            for exp in experiences:
                if abs(exp.execution_time - mean_time) > 2 * std_time:
                    anomalies.append(exp.experience_id)
        
        return anomalies
    
    def _extract_patterns(self, experiences: List[LearningExperience]) -> List[str]:
        """Extract common patterns from experiences"""
        patterns = []
        
        # Group by task type and success
        success_patterns = {}
        failure_patterns = {}
        
        for exp in experiences:
            key = exp.task_type
            if exp.success:
                if key not in success_patterns:
                    success_patterns[key] = []
                success_patterns[key].extend(exp.learned_patterns)
            else:
                if key not in failure_patterns:
                    failure_patterns[key] = []
                failure_patterns[key].extend(exp.improvement_suggestions)
        
        # Extract common patterns
        for task_type, patterns_list in success_patterns.items():
            if patterns_list:
                common_pattern = max(set(patterns_list), key=patterns_list.count)
                patterns.append(f"Success pattern for {task_type}: {common_pattern}")
        
        for task_type, suggestions in failure_patterns.items():
            if suggestions:
                common_suggestion = max(set(suggestions), key=suggestions.count)
                patterns.append(f"Improvement for {task_type}: {common_suggestion}")
        
        return patterns
    
    def _find_optimization_opportunities(self, experiences: List[LearningExperience]) -> List[str]:
        """Find opportunities for optimization"""
        opportunities = []
        
        # Analyze resource usage patterns
        high_cpu_experiences = [exp for exp in experiences if exp.resource_usage.get("cpu", 0) > 80]
        high_memory_experiences = [exp for exp in experiences if exp.resource_usage.get("memory", 0) > 1000]  # MB
        
        if high_cpu_experiences:
            opportunities.append(f"Optimize CPU usage for {len(high_cpu_experiences)} experiences")
        
        if high_memory_experiences:
            opportunities.append(f"Optimize memory usage for {len(high_memory_experiences)} experiences")
        
        # Analyze failure patterns
        failures = [exp for exp in experiences if not exp.success]
        if failures:
            opportunities.append(f"Reduce failure rate by analyzing {len(failures)} failed experiences")
        
        return opportunities

class ReinforcementLearning(LearningAlgorithm):
    """Reinforcement learning for decision optimization"""
    
    def __init__(self):
        self.q_table = {}
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.exploration_rate = 0.1
    
    async def learn(self, experiences: List[LearningExperience]) -> Dict[str, Any]:
        """Update Q-table based on experiences"""
        try:
            improvements = {}
            
            for exp in experiences:
                # Create state-action pairs
                state = self._create_state(exp)
                action = self._create_action(exp)
                reward = self._calculate_reward(exp)
                
                # Update Q-table
                if state not in self.q_table:
                    self.q_table[state] = {}
                
                if action not in self.q_table[state]:
                    self.q_table[state][action] = 0.0
                
                # Q-learning update
                old_value = self.q_table[state][action]
                max_future_reward = max(self.q_table.get(state, {}).values()) if self.q_table.get(state) else 0
                new_value = (1 - self.learning_rate) * old_value + self.learning_rate * (reward + self.discount_factor * max_future_reward)
                
                self.q_table[state][action] = new_value
            
            improvements = {
                "q_table_size": len(self.q_table),
                "learning_rate": self.learning_rate,
                "discount_factor": self.discount_factor,
                "exploration_rate": self.exploration_rate,
                "optimized_decisions": self._get_optimized_decisions()
            }
            
            return improvements
            
        except Exception as e:
            logger.error(f"Reinforcement learning failed: {e}")
            return {}
    
    async def adapt(self, current_state: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt Q-table with new experiences"""
        try:
            if "experiences" in new_data:
                await self.learn(new_data["experiences"])
            
            return current_state
            
        except Exception as e:
            logger.error(f"Reinforcement learning adaptation failed: {e}")
            return current_state
    
    def _create_state(self, experience: LearningExperience) -> str:
        """Create state representation"""
        return f"{experience.task_type}_{int(experience.execution_time // 60)}min_{experience.resource_usage.get('cpu', 0)}cpu"
    
    def _create_action(self, experience: LearningExperience) -> str:
        """Create action representation"""
        if experience.success:
            return "success"
        else:
            return "failure"
    
    def _calculate_reward(self, experience: LearningExperience) -> float:
        """Calculate reward for experience"""
        base_reward = 1.0 if experience.success else -1.0
        
        # Adjust reward based on execution time and resource usage
        time_penalty = experience.execution_time / 3600  # Normalize to hours
        resource_penalty = (experience.resource_usage.get("cpu", 0) + experience.resource_usage.get("memory", 0) / 100) / 200
        
        return base_reward - time_penalty - resource_penalty
    
    def _get_optimized_decisions(self) -> Dict[str, str]:
        """Get optimized decisions based on Q-table"""
        decisions = {}
        
        for state, actions in self.q_table.items():
            if actions:
                best_action = max(actions, key=actions.get)
                decisions[state] = best_action
        
        return decisions

class SelfImprovementEngine:
    """Main self-improvement engine"""
    
    def __init__(self):
        self.is_running = False
        self.learning_algorithms = {
            LearningType.SUPERVISED: SupervisedLearning(),
            LearningType.UNSUPERVISED: UnsupervisedLearning(),
            LearningType.REINFORCEMENT: ReinforcementLearning(),
        }
        
        # Learning history and metrics
        self.learning_history: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, PerformanceMetric] = {}
        self.improvement_actions: List[ImprovementAction] = []
        
        # Configuration
        self.learning_interval = 3600  # 1 hour
        self.memory_retention_days = 30
        self.improvement_threshold = 0.8  # 80% success rate threshold
        self.auto_improve = True
        
        # Experience storage
        self.experiences: List[LearningExperience] = []
        self.experience_buffer_size = 1000
    
    async def start(self):
        """Start the self-improvement engine"""
        logger.info("Starting Self-Improvement Engine...")
        self.is_running = True
        
        # Load existing data
        await self._load_learning_data()
        
        # Start background learning loop
        asyncio.create_task(self._learning_loop())
        
        logger.info("Self-Improvement Engine started successfully")
    
    async def stop(self):
        """Stop the self-improvement engine"""
        logger.info("Stopping Self-Improvement Engine...")
        self.is_running = False
        
        # Save learning data
        await self._save_learning_data()
        
        logger.info("Self-Improvement Engine stopped")
    
    async def record_experience(self, task_id: str, task_description: str, task_type: str,
                              success: bool, execution_time: float, resource_usage: Dict[str, float],
                              error_details: Optional[str] = None) -> str:
        """Record a learning experience from task execution"""
        try:
            # Create experience
            experience = LearningExperience(
                experience_id=f"exp_{int(datetime.utcnow().timestamp())}_{hash(task_id) % 10000}",
                task_id=task_id,
                task_description=task_description,
                task_type=task_type,
                success=success,
                execution_time=execution_time,
                resource_usage=resource_usage,
                error_details=error_details
            )
            
            # Analyze experience for patterns and suggestions
            experience.learned_patterns = await self._analyze_patterns(experience)
            experience.improvement_suggestions = await self._generate_suggestions(experience)
            
            # Add to experiences
            self.experiences.append(experience)
            
            # Limit buffer size
            if len(self.experiences) > self.experience_buffer_size:
                self.experiences.pop(0)
            
            # Store in database
            await self._store_experience(experience)
            
            logger.info(f"Recorded learning experience: {experience.experience_id}")
            return experience.experience_id
            
        except Exception as e:
            logger.error(f"Failed to record experience: {e}")
            return ""
    
    async def trigger_learning(self) -> Dict[str, Any]:
        """Trigger learning process manually"""
        try:
            if not self.experiences:
                logger.warning("No experiences available for learning")
                return {"success": False, "message": "No experiences available"}
            
            # Perform learning with all algorithms
            learning_results = {}
            
            for learning_type, algorithm in self.learning_algorithms.items():
                try:
                    improvements = await algorithm.learn(self.experiences)
                    learning_results[learning_type.value] = improvements
                except Exception as e:
                    logger.error(f"Learning failed for {learning_type}: {e}")
                    learning_results[learning_type.value] = {"error": str(e)}
            
            # Generate improvement actions
            improvement_actions = await self._generate_improvement_actions(learning_results)
            
            # Update performance metrics
            await self._update_performance_metrics()
            
            # Save learning results
            learning_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "experience_count": len(self.experiences),
                "learning_results": learning_results,
                "improvement_actions": [action.action_id for action in improvement_actions]
            }
            
            self.learning_history.append(learning_record)
            
            logger.info(f"Learning completed with {len(learning_results)} algorithms")
            return {
                "success": True,
                "learning_results": learning_results,
                "improvement_actions": len(improvement_actions),
                "experience_count": len(self.experiences)
            }
            
        except Exception as e:
            logger.error(f"Learning trigger failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def apply_improvements(self) -> Dict[str, Any]:
        """Apply generated improvements to the system"""
        try:
            improvements_applied = 0
            failed_improvements = 0
            
            for action in self.improvement_actions:
                if action.status == "pending":
                    try:
                        success = await self._apply_improvement_action(action)
                        if success:
                            action.status = "completed"
                            action.completed_at = datetime.utcnow()
                            improvements_applied += 1
                        else:
                            action.status = "failed"
                            failed_improvements += 1
                    except Exception as e:
                        logger.error(f"Failed to apply improvement {action.action_id}: {e}")
                        action.status = "failed"
                        failed_improvements += 1
            
            logger.info(f"Applied {improvements_applied} improvements, {failed_improvements} failed")
            return {
                "success": True,
                "improvements_applied": improvements_applied,
                "failed_improvements": failed_improvements,
                "total_actions": len(self.improvement_actions)
            }
            
        except Exception as e:
            logger.error(f"Improvement application failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        try:
            # Calculate overall success rate
            total_experiences = len(self.experiences)
            successful_experiences = sum(1 for exp in self.experiences if exp.success)
            success_rate = successful_experiences / total_experiences if total_experiences > 0 else 0
            
            # Calculate average execution time
            avg_execution_time = statistics.mean([exp.execution_time for exp in self.experiences]) if self.experiences else 0
            
            # Get recent learning results
            recent_learning = self.learning_history[-5:] if self.learning_history else []
            
            # Get active improvement actions
            active_actions = [action for action in self.improvement_actions if action.status == "in_progress"]
            
            report = {
                "timestamp": datetime.utcnow().isoformat(),
                "total_experiences": total_experiences,
                "success_rate": success_rate,
                "average_execution_time": avg_execution_time,
                "performance_metrics": {k: v.value for k, v in self.performance_metrics.items()},
                "recent_learning": recent_learning,
                "active_improvements": len(active_actions),
                "completed_improvements": len([a for a in self.improvement_actions if a.status == "completed"]),
                "failed_improvements": len([a for a in self.improvement_actions if a.status == "failed"]),
                "recommendations": await self._generate_recommendations()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Performance report generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    # Helper methods
    
    async def _learning_loop(self):
        """Background learning loop"""
        while self.is_running:
            try:
                if self.experiences and self.auto_improve:
                    await self.trigger_learning()
                    await self.apply_improvements()
                
                await asyncio.sleep(self.learning_interval)
                
            except Exception as e:
                logger.error(f"Learning loop error: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retrying
    
    async def _analyze_patterns(self, experience: LearningExperience) -> List[str]:
        """Analyze experience for patterns"""
        patterns = []
        
        # Pattern based on task type and success
        if experience.success:
            patterns.append(f"Successful {experience.task_type} task")
        else:
            patterns.append(f"Failed {experience.task_type} task")
        
        # Pattern based on execution time
        if experience.execution_time < 60:
            patterns.append("Fast execution")
        elif experience.execution_time < 600:
            patterns.append("Medium execution")
        else:
            patterns.append("Slow execution")
        
        # Pattern based on resource usage
        cpu_usage = experience.resource_usage.get("cpu", 0)
        memory_usage = experience.resource_usage.get("memory", 0)
        
        if cpu_usage > 80:
            patterns.append("High CPU usage")
        if memory_usage > 1000:
            patterns.append("High memory usage")
        
        return patterns
    
    async def _generate_suggestions(self, experience: LearningExperience) -> List[str]:
        """Generate improvement suggestions based on experience"""
        suggestions = []
        
        if not experience.success:
            suggestions.append("Review task planning and execution strategy")
        
        if experience.execution_time > 600:  # 10 minutes
            suggestions.append("Optimize execution time")
        
        if experience.resource_usage.get("cpu", 0) > 80:
            suggestions.append("Reduce CPU usage")
        
        if experience.resource_usage.get("memory", 0) > 1000:  # 1GB
            suggestions.append("Reduce memory usage")
        
        return suggestions
    
    async def _generate_improvement_actions(self, learning_results: Dict[str, Any]) -> List[ImprovementAction]:
        """Generate improvement actions based on learning results"""
        actions = []
        
        for learning_type, results in learning_results.items():
            if isinstance(results, dict):
                # Generate actions based on learning type
                if learning_type == "supervised":
                    actions.extend(self._generate_supervised_actions(results))
                elif learning_type == "unsupervised":
                    actions.extend(self._generate_unsupervised_actions(results))
                elif learning_type == "reinforcement":
                    actions.extend(self._generate_reinforcement_actions(results))
        
        # Sort actions by priority and impact
        actions.sort(key=lambda x: (x.priority, x.estimated_impact), reverse=True)
        
        return actions
    
    def _generate_supervised_actions(self, results: Dict[str, Any]) -> List[ImprovementAction]:
        """Generate actions from supervised learning results"""
        actions = []
        
        if "success_prediction_accuracy" in results:
            accuracy = results["success_prediction_accuracy"]
            if accuracy < 0.8:
                actions.append(ImprovementAction(
                    action_id=f"supervised_accuracy_{int(datetime.utcnow().timestamp())}",
                    type=ImprovementType.PERFORMANCE,
                    description="Improve success prediction accuracy",
                    priority=8,
                    estimated_impact=0.7,
                    implementation_cost=0.3
                ))
        
        return actions
    
    def _generate_unsupervised_actions(self, results: Dict[str, Any]) -> List[ImprovementAction]:
        """Generate actions from unsupervised learning results"""
        actions = []
        
        if "optimization_opportunities" in results:
            opportunities = results["optimization_opportunities"]
            for opportunity in opportunities:
                actions.append(ImprovementAction(
                    action_id=f"unsupervised_opt_{int(datetime.utcnow().timestamp())}_{len(actions)}",
                    type=ImprovementType.EFFICIENCY,
                    description=opportunity,
                    priority=6,
                    estimated_impact=0.5,
                    implementation_cost=0.4
                ))
        
        return actions
    
    def _generate_reinforcement_actions(self, results: Dict[str, Any]) -> List[ImprovementAction]:
        """Generate actions from reinforcement learning results"""
        actions = []
        
        if "q_table_size" in results:
            q_table_size = results["q_table_size"]
            if q_table_size > 1000:
                actions.append(ImprovementAction(
                    action_id=f"reinforcement_opt_{int(datetime.utcnow().timestamp())}",
                    type=ImprovementType.ADAPTABILITY,
                    description="Optimize Q-table size and learning parameters",
                    priority=7,
                    estimated_impact=0.6,
                    implementation_cost=0.5
                ))
        
        return actions
    
    async def _apply_improvement_action(self, action: ImprovementAction) -> bool:
        """Apply a specific improvement action"""
        try:
            # Implementation would depend on action type
            if action.type == ImprovementType.PERFORMANCE:
                return await self._apply_performance_improvement(action)
            elif action.type == ImprovementType.EFFICIENCY:
                return await self._apply_efficiency_improvement(action)
            elif action.type == ImprovementType.ADAPTABILITY:
                return await self._apply_adaptability_improvement(action)
            else:
                logger.warning(f"Unknown improvement type: {action.type}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to apply improvement {action.action_id}: {e}")
            return False
    
    async def _apply_performance_improvement(self, action: ImprovementAction) -> bool:
        """Apply performance improvement"""
        # Implementation would modify system parameters
        logger.info(f"Applying performance improvement: {action.description}")
        return True
    
    async def _apply_efficiency_improvement(self, action: ImprovementAction) -> bool:
        """Apply efficiency improvement"""
        # Implementation would optimize resource usage
        logger.info(f"Applying efficiency improvement: {action.description}")
        return True
    
    async def _apply_adaptability_improvement(self, action: ImprovementAction) -> bool:
        """Apply adaptability improvement"""
        # Implementation would improve learning algorithms
        logger.info(f"Applying adaptability improvement: {action.description}")
        return True
    
    async def _update_performance_metrics(self):
        """Update performance metrics based on recent experiences"""
        if not self.experiences:
            return
        
        # Calculate success rate
        recent_experiences = self.experiences[-100:]  # Last 100 experiences
        success_rate = sum(1 for exp in recent_experiences if exp.success) / len(recent_experiences)
        
        # Update or create success rate metric
        if "success_rate" not in self.performance_metrics:
            self.performance_metrics["success_rate"] = PerformanceMetric(
                metric_id="success_rate",
                name="Task Success Rate",
                value=success_rate,
                target=0.9,
                trend=[success_rate]
            )
        else:
            metric = self.performance_metrics["success_rate"]
            metric.value = success_rate
            metric.trend.append(success_rate)
            metric.last_updated = datetime.utcnow()
    
    async def _store_experience(self, experience: LearningExperience):
        """Store experience in database"""
        try:
            async with AsyncSessionLocal() as db:
                memory_entry = MemoryStore(
                    agent_id="god_agi",
                    content=json.dumps({
                        "experience_id": experience.experience_id,
                        "task_id": experience.task_id,
                        "task_description": experience.task_description,
                        "task_type": experience.task_type,
                        "success": experience.success,
                        "execution_time": experience.execution_time,
                        "resource_usage": experience.resource_usage,
                        "error_details": experience.error_details,
                        "learned_patterns": experience.learned_patterns,
                        "improvement_suggestions": experience.improvement_suggestions
                    }),
                    created_at=experience.timestamp
                )
                db.add(memory_entry)
                await db.commit()
        except Exception as e:
            logger.error(f"Failed to store experience: {e}")
    
    async def _load_learning_data(self):
        """Load learning data from database"""
        try:
            # Load experiences from database
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    "SELECT content FROM memory_store WHERE agent_id = 'god_agi' ORDER BY created_at DESC LIMIT 1000"
                )
                stored_experiences = result.fetchall()
                
                for exp_data in stored_experiences:
                    try:
                        data = json.loads(exp_data[0])
                        experience = LearningExperience(
                            experience_id=data["experience_id"],
                            task_id=data["task_id"],
                            task_description=data["task_description"],
                            task_type=data["task_type"],
                            success=data["success"],
                            execution_time=data["execution_time"],
                            resource_usage=data["resource_usage"],
                            error_details=data.get("error_details"),
                            learned_patterns=data.get("learned_patterns", []),
                            improvement_suggestions=data.get("improvement_suggestions", [])
                        )
                        self.experiences.append(experience)
                    except Exception as e:
                        logger.error(f"Failed to load experience: {e}")
                
                logger.info(f"Loaded {len(self.experiences)} experiences from database")
                
        except Exception as e:
            logger.error(f"Failed to load learning data: {e}")
    
    async def _save_learning_data(self):
        """Save learning data to database"""
        try:
            # Save recent experiences
            async with AsyncSessionLocal() as db:
                for experience in self.experiences[-100:]:  # Save last 100 experiences
                    # Check if already stored
                    existing = await db.execute(
                        "SELECT id FROM memory_store WHERE content LIKE :content",
                        {"content": f"%{experience.experience_id}%"}
                    )
                    if not existing.fetchone():
                        memory_entry = MemoryStore(
                            agent_id="god_agi",
                            content=json.dumps({
                                "experience_id": experience.experience_id,
                                "task_id": experience.task_id,
                                "task_description": experience.task_description,
                                "task_type": experience.task_type,
                                "success": experience.success,
                                "execution_time": experience.execution_time,
                                "resource_usage": experience.resource_usage,
                                "error_details": experience.error_details,
                                "learned_patterns": experience.learned_patterns,
                                "improvement_suggestions": experience.improvement_suggestions
                            }),
                            created_at=experience.timestamp
                        )
                        db.add(memory_entry)
                
                await db.commit()
                
        except Exception as e:
            logger.error(f"Failed to save learning data: {e}")
    
    async def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on performance analysis"""
        recommendations = []
        
        # Analyze success rate
        if "success_rate" in self.performance_metrics:
            success_rate = self.performance_metrics["success_rate"].value
            if success_rate < 0.8:
                recommendations.append("Focus on improving task success rate through better planning")
        
        # Analyze recent learning results
        if self.learning_history:
            recent_results = self.learning_history[-1]
            if "unsupervised" in recent_results.get("learning_results", {}):
                unsupervised_results = recent_results["learning_results"]["unsupervised"]
                if "optimization_opportunities" in unsupervised_results:
                    opportunities = unsupervised_results["optimization_opportunities"]
                    for opportunity in opportunities[:3]:  # Top 3 opportunities
                        recommendations.append(f"Address optimization opportunity: {opportunity}")
        
        return recommendations

# Global self-improvement engine instance
self_improvement_engine = SelfImprovementEngine()

# Convenience functions for external use
async def record_experience(task_id: str, task_description: str, task_type: str,
                          success: bool, execution_time: float, resource_usage: Dict[str, float],
                          error_details: Optional[str] = None) -> str:
    """Record a learning experience"""
    return await self_improvement_engine.record_experience(
        task_id, task_description, task_type, success, execution_time, 
        resource_usage, error_details
    )

async def trigger_learning() -> Dict[str, Any]:
    """Trigger learning process"""
    return await self_improvement_engine.trigger_learning()

async def apply_improvements() -> Dict[str, Any]:
    """Apply generated improvements"""
    return await self_improvement_engine.apply_improvements()

async def get_performance_report() -> Dict[str, Any]:
    """Get performance report"""
    return await self_improvement_engine.get_performance_report()