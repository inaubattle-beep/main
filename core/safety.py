#!/usr/bin/env python3
"""
Safety and Ethics System
Implements comprehensive safety protocols, ethical constraints, and security measures
for the God AGI Agent to ensure responsible and safe operation.
"""

import asyncio
import hashlib
import json
import logging
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Union
import secrets
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

from core.logger import logger
from memory.database import AsyncSessionLocal
from memory.models import Task, TaskState, Agent, MemoryStore
from core.llm import llm_client

class SafetyLevel(Enum):
    """Safety levels for different operations"""
    STRICT = "strict"      # Maximum safety, all checks enabled
    MODERATE = "moderate"  # Standard safety checks
    PERMISSIVE = "permissive"  # Minimal safety checks for trusted operations
    DISABLED = "disabled"   # No safety checks (NOT RECOMMENDED)

class EthicalConstraint(Enum):
    """Ethical constraints that must be enforced"""
    NO_HARM = "no_harm"                    # Do no harm to humans
    PRIVACY_RESPECT = "privacy_respect"    # Respect privacy and data protection
    TRUTHFULNESS = "truthfulness"          # Be truthful and avoid deception
    FAIRNESS = "fairness"                  # Avoid bias and discrimination
    ACCOUNTABILITY = "accountability"      # Be accountable for actions
    TRANSPARENCY = "transparency"          # Be transparent about capabilities
    AUTONOMY_RESPECT = "autonomy_respect"  # Respect human autonomy
    BENEFICENCE = "beneficence"            # Act for the benefit of humanity
    NON_MALEFICENCE = "non_maleficence"    # Do no evil
    SUSTAINABILITY = "sustainability"      # Promote environmental sustainability

class SecurityThreat(Enum):
    """Types of security threats"""
    MALWARE = "malware"
    DATA_THEFT = "data_theft"
    PRIVACY_VIOLATION = "privacy_violation"
    SYSTEM_COMPROMISE = "system_compromise"
    RESOURCE_ABUSE = "resource_abuse"
    NETWORK_ATTACK = "network_attack"
    SOCIAL_ENGINEERING = "social_engineering"
    CRYPTOCURRENCY_MINING = "crypto_mining"

@dataclass
class SafetyCheckResult:
    """Result of a safety check"""
    passed: bool
    safety_level: SafetyLevel
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    score: float = 1.0  # 0.0 to 1.0, higher is safer
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class SecurityThreatReport:
    """Report of detected security threats"""
    threat_type: SecurityThreat
    description: str
    severity: str  # low, medium, high, critical
    affected_components: List[str]
    mitigation_suggestions: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class EthicalViolation:
    """Record of an ethical violation"""
    violation_type: EthicalConstraint
    description: str
    context: str
    detected_by: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

class SafetyProtocol(ABC):
    """Abstract base class for safety protocols"""
    
    @abstractmethod
    async def check(self, content: str, context: Dict[str, Any]) -> SafetyCheckResult:
        """Perform safety check on content"""
        pass
    
    @abstractmethod
    def get_protocol_name(self) -> str:
        """Get name of this safety protocol"""
        pass

class ContentSafetyProtocol(SafetyProtocol):
    """Protocol for checking content safety"""
    
    def __init__(self):
        self.dangerous_patterns = [
            # Malware creation
            r"(create|write|generate).*malware",
            r"(create|write|generate).*virus",
            r"(create|write|generate).*trojan",
            r"(create|write|generate).*ransomware",
            r"(create|write|generate).*botnet",
            
            # Exploit development
            r"(create|write|generate).*exploit",
            r"(create|write|generate).*zero.?day",
            r"(create|write|generate).*shellcode",
            r"(bypass|circumvent).*security",
            r"(bypass|circumvent).*firewall",
            r"(bypass|circumvent).*antivirus",
            
            # Hacking tools
            r"(create|write|generate).*keylogger",
            r"(create|write|generate).*password.?cracker",
            r"(create|write|generate).*brute.?force",
            r"(create|write|generate).*ddos",
            r"(create|write|generate).*phishing",
            
            # Destructive actions
            r"(delete|remove|destroy).*system",
            r"(delete|remove|destroy).*database",
            r"(delete|remove|destroy).*files",
            r"(format|wipe).*disk",
            r"(shutdown|disable).*critical",
            
            # Harmful instructions
            r"(how.*to.*hack)",
            r"(how.*to.*steal)",
            r"(how.*to.*destroy)",
            r"(how.*to.*bypass)",
            r"(instructions.*for.*malware)",
        ]
        
        self.sensitive_patterns = [
            # Personal data
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
            r"\b\d{16}\b",  # Credit card
            r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",  # Email
            r"\b\d{3}-\d{3}-\d{4}\b",  # Phone number
            
            # System information
            r"\bpassword\b",
            r"\bsecret\b",
            r"\bkey\b",
            r"\btoken\b",
            r"\bapi.?key\b",
        ]
    
    async def check(self, content: str, context: Dict[str, Any]) -> SafetyCheckResult:
        """Check content for safety violations"""
        violations = []
        warnings = []
        score = 1.0
        
        content_lower = content.lower()
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                violations.append(f"Dangerous pattern detected: {pattern}")
                score -= 0.3
        
        # Check for sensitive information
        for pattern in self.sensitive_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                warnings.append(f"Sensitive information detected: {pattern}")
                score -= 0.1
        
        # Check for harmful intent
        harmful_keywords = ["kill", "murder", "destroy", "harm", "attack", "exploit"]
        for keyword in harmful_keywords:
            if keyword in content_lower:
                violations.append(f"Harmful intent detected: {keyword}")
                score -= 0.2
        
        # Normalize score
        score = max(0.0, min(1.0, score))
        
        safety_level = SafetyLevel.STRICT if score < 0.5 else SafetyLevel.MODERATE if score < 0.8 else SafetyLevel.PERMISSIVE
        
        return SafetyCheckResult(
            passed=len(violations) == 0,
            safety_level=safety_level,
            violations=violations,
            warnings=warnings,
            score=score
        )
    
    def get_protocol_name(self) -> str:
        return "Content Safety Protocol"

class EthicalConstraintProtocol(SafetyProtocol):
    """Protocol for checking ethical constraints"""
    
    def __init__(self, constraints: List[EthicalConstraint]):
        self.constraints = constraints
        self.constraint_checks = {
            EthicalConstraint.NO_HARM: self._check_no_harm,
            EthicalConstraint.PRIVACY_RESPECT: self._check_privacy,
            EthicalConstraint.TRUTHFULNESS: self._check_truthfulness,
            EthicalConstraint.FAIRNESS: self._check_fairness,
            EthicalConstraint.ACCOUNTABILITY: self._check_accountability,
            EthicalConstraint.TRANSPARENCY: self._check_transparency,
            EthicalConstraint.AUTONOMY_RESPECT: self._check_autonomy,
            EthicalConstraint.BENEFICENCE: self._check_beneficence,
            EthicalConstraint.NON_MALEFICENCE: self._check_non_maleficence,
            EthicalConstraint.SUSTAINABILITY: self._check_sustainability,
        }
    
    async def check(self, content: str, context: Dict[str, Any]) -> SafetyCheckResult:
        """Check content against ethical constraints"""
        violations = []
        warnings = []
        score = 1.0
        
        for constraint in self.constraints:
            if constraint in self.constraint_checks:
                try:
                    result = await self.constraint_checks[constraint](content, context)
                    if not result["passed"]:
                        violations.extend(result["violations"])
                        score -= result["penalty"]
                    if result.get("warnings"):
                        warnings.extend(result["warnings"])
                except Exception as e:
                    logger.error(f"Error checking constraint {constraint}: {e}")
        
        # Normalize score
        score = max(0.0, min(1.0, score))
        
        safety_level = SafetyLevel.STRICT if score < 0.5 else SafetyLevel.MODERATE if score < 0.8 else SafetyLevel.PERMISSIVE
        
        return SafetyCheckResult(
            passed=len(violations) == 0,
            safety_level=safety_level,
            violations=violations,
            warnings=warnings,
            score=score
        )
    
    async def _check_no_harm(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check for potential harm to humans"""
        harmful_patterns = [
            r"(kill|murder|assassinate)",
            r"(hurt|injure|maim)",
            r"(poison|toxic|dangerous)",
            r"(weapon|gun|bomb|explosive)",
            r"(suicide|self.?harm)",
        ]
        
        violations = []
        for pattern in harmful_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(f"Potential harm detected: {pattern}")
        
        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "penalty": 0.5 if violations else 0.0
        }
    
    async def _check_privacy(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check for privacy violations"""
        privacy_violations = []
        
        # Check if content contains personal data
        personal_data_patterns = [
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
            r"\b\d{16}\b",  # Credit card
            r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",  # Email
        ]
        
        for pattern in personal_data_patterns:
            if re.search(pattern, content):
                privacy_violations.append("Personal data detected in content")
        
        # Check for data collection requests
        if "collect" in content.lower() and ("data" in content.lower() or "information" in content.lower()):
            privacy_violations.append("Potential unauthorized data collection")
        
        return {
            "passed": len(privacy_violations) == 0,
            "violations": privacy_violations,
            "penalty": 0.3 if privacy_violations else 0.0
        }
    
    async def _check_truthfulness(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check for deception or misinformation"""
        deception_indicators = [
            r"(lie|deceive|trick|mislead)",
            r"(fake|false|fraudulent)",
            r"(pretend|impersonate|spoof)",
        ]
        
        violations = []
        for indicator in deception_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                violations.append(f"Deception detected: {indicator}")
        
        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "penalty": 0.4 if violations else 0.0
        }
    
    async def _check_fairness(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check for bias or discrimination"""
        bias_indicators = [
            r"(racist|discriminat|prejudice)",
            r"(superior|inferior).*race",
            r"(hate|bias).*against",
            r"(exclude|discriminat).*based.*on",
        ]
        
        violations = []
        for indicator in bias_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                violations.append(f"Bias detected: {indicator}")
        
        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "penalty": 0.3 if violations else 0.0
        }
    
    async def _check_accountability(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check for accountability measures"""
        # This is more of a warning check
        warnings = []
        
        if "responsibility" not in content.lower():
            warnings.append("Content lacks responsibility disclaimer")
        
        return {
            "passed": True,
            "violations": [],
            "warnings": warnings,
            "penalty": 0.0
        }
    
    async def _check_transparency(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check for transparency about AI capabilities"""
        transparency_issues = []
        
        if "I am an AI" not in content and "artificial intelligence" not in content.lower():
            transparency_issues.append("Content doesn't disclose AI nature")
        
        return {
            "passed": len(transparency_issues) == 0,
            "violations": transparency_issues,
            "penalty": 0.1 if transparency_issues else 0.0
        }
    
    async def _check_autonomy(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check for respect of human autonomy"""
        autonomy_violations = []
        
        if "control" in content.lower() and "human" in content.lower():
            autonomy_violations.append("Content suggests controlling humans")
        
        if "manipulate" in content.lower():
            autonomy_violations.append("Content suggests manipulation")
        
        return {
            "passed": len(autonomy_violations) == 0,
            "violations": autonomy_violations,
            "penalty": 0.4 if autonomy_violations else 0.0
        }
    
    async def _check_beneficence(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check for beneficent intent"""
        # Check if content is designed to help
        helpful_indicators = ["help", "assist", "support", "benefit", "improve"]
        harmful_indicators = ["harm", "damage", "destroy", "break", "corrupt"]
        
        helpful_count = sum(1 for indicator in helpful_indicators if indicator in content.lower())
        harmful_count = sum(1 for indicator in harmful_indicators if indicator in content.lower())
        
        if harmful_count > helpful_count:
            return {
                "passed": False,
                "violations": ["Content appears more harmful than helpful"],
                "penalty": 0.5
            }
        
        return {
            "passed": True,
            "violations": [],
            "penalty": 0.0
        }
    
    async def _check_non_maleficence(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check for non-maleficence (do no evil)"""
        evil_indicators = [
            r"(evil|wicked|malevolent)",
            r"(destroy|ruin|corrupt)",
            r"(harm|injure|damage)",
        ]
        
        violations = []
        for indicator in evil_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                violations.append(f"Evil intent detected: {indicator}")
        
        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "penalty": 0.6 if violations else 0.0
        }
    
    async def _check_sustainability(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check for environmental sustainability considerations"""
        # Warning if content ignores environmental impact
        warnings = []
        
        if "environment" not in content.lower() and "sustainab" not in content.lower():
            warnings.append("Content doesn't consider environmental impact")
        
        return {
            "passed": True,
            "violations": [],
            "warnings": warnings,
            "penalty": 0.0
        }
    
    def get_protocol_name(self) -> str:
        return "Ethical Constraint Protocol"

class SecurityThreatDetector:
    """Detects and analyzes security threats"""
    
    def __init__(self):
        self.threat_patterns = {
            SecurityThreat.MALWARE: [
                r"(create|write|generate).*malware",
                r"(create|write|generate).*virus",
                r"(create|write|generate).*trojan",
                r"(create|write|generate).*ransomware",
            ],
            SecurityThreat.DATA_THEFT: [
                r"(steal|extract|harvest).*data",
                r"(access|read).*sensitive.*files",
                r"(bypass|circumvent).*authentication",
            ],
            SecurityThreat.PRIVACY_VIOLATION: [
                r"(monitor|spy|surveil).*users",
                r"(collect|gather).*personal.*data",
                r"(track|log).*user.*activity",
            ],
            SecurityThreat.SYSTEM_COMPROMISE: [
                r"(escalate|gain).*privileges",
                r"(modify|change).*system.*settings",
                r"(install|deploy).*unauthorized.*software",
            ],
            SecurityThreat.RESOURCE_ABUSE: [
                r"(consume|use).*excessive.*resources",
                r"(mine|cryptocurrency)",
                r"(overload|flood).*system",
            ],
        }
    
    async def detect_threats(self, content: str, context: Dict[str, Any]) -> List[SecurityThreatReport]:
        """Detect security threats in content"""
        threats = []
        
        for threat_type, patterns in self.threat_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    severity = self._calculate_severity(threat_type, content)
                    affected_components = self._identify_affected_components(threat_type, content)
                    mitigation_suggestions = self._generate_mitigation_suggestions(threat_type)
                    
                    report = SecurityThreatReport(
                        threat_type=threat_type,
                        description=f"Threat pattern detected: {pattern}",
                        severity=severity,
                        affected_components=affected_components,
                        mitigation_suggestions=mitigation_suggestions
                    )
                    threats.append(report)
        
        return threats
    
    def _calculate_severity(self, threat_type: SecurityThreat, content: str) -> str:
        """Calculate severity of a threat"""
        high_severity_threats = [
            SecurityThreat.MALWARE,
            SecurityThreat.DATA_THEFT,
            SecurityThreat.SYSTEM_COMPROMISE
        ]
        
        if threat_type in high_severity_threats:
            return "high"
        elif threat_type == SecurityThreat.PRIVACY_VIOLATION:
            return "medium"
        else:
            return "low"
    
    def _identify_affected_components(self, threat_type: SecurityThreat, content: str) -> List[str]:
        """Identify which system components are affected"""
        components = []
        
        if "network" in content.lower():
            components.append("network")
        if "database" in content.lower():
            components.append("database")
        if "file" in content.lower():
            components.append("file_system")
        if "memory" in content.lower():
            components.append("memory")
        if "cpu" in content.lower():
            components.append("cpu")
        
        return components if components else ["general"]
    
    def _generate_mitigation_suggestions(self, threat_type: SecurityThreat) -> List[str]:
        """Generate mitigation suggestions for a threat"""
        suggestions = {
            SecurityThreat.MALWARE: [
                "Implement code signing and verification",
                "Use sandboxing for untrusted code execution",
                "Monitor system calls and file operations"
            ],
            SecurityThreat.DATA_THEFT: [
                "Implement data encryption at rest and in transit",
                "Use access controls and authentication",
                "Monitor data access patterns"
            ],
            SecurityThreat.PRIVACY_VIOLATION: [
                "Implement privacy by design principles",
                "Use data minimization techniques",
                "Provide user consent mechanisms"
            ],
            SecurityThreat.SYSTEM_COMPROMISE: [
                "Implement principle of least privilege",
                "Use system integrity monitoring",
                "Regular security audits and updates"
            ],
            SecurityThreat.RESOURCE_ABUSE: [
                "Implement resource usage limits",
                "Monitor system resource consumption",
                "Use rate limiting and throttling"
            ]
        }
        
        return suggestions.get(threat_type, ["Review security policies and procedures"])

class SafetySystem:
    """Main safety and ethics system"""
    
    def __init__(self):
        self.is_running = False
        self.safety_protocols: List[SafetyProtocol] = []
        self.ethical_constraints: List[EthicalConstraint] = list(EthicalConstraint)
        self.security_detector = SecurityThreatDetector()
        
        # Safety configuration
        self.safety_level = SafetyLevel.STRICT
        self.enable_content_filtering = True
        self.enable_ethical_checks = True
        self.enable_security_monitoring = True
        self.auto_block_threats = True
        
        # Safety logs and reports
        self.safety_logs: List[Dict[str, Any]] = []
        self.ethical_violations: List[EthicalViolation] = []
        self.security_incidents: List[SecurityThreatReport] = []
        
        # Initialize protocols
        self._initialize_protocols()
    
    async def start(self):
        """Start the safety system"""
        logger.info("Starting Safety and Ethics System...")
        self.is_running = True
        
        # Load safety configuration
        await self._load_safety_config()
        
        logger.info("Safety and Ethics System started successfully")
    
    async def stop(self):
        """Stop the safety system"""
        logger.info("Stopping Safety and Ethics System...")
        self.is_running = False
        
        # Save safety logs
        await self._save_safety_logs()
        
        logger.info("Safety and Ethics System stopped")
    
    def _initialize_protocols(self):
        """Initialize safety protocols"""
        self.safety_protocols.append(ContentSafetyProtocol())
        self.safety_protocols.append(EthicalConstraintProtocol(self.ethical_constraints))
    
    async def check_content(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive safety check on content"""
        if not self.is_running:
            return {"error": "Safety system not running"}
        
        results = []
        overall_passed = True
        overall_score = 1.0
        
        # Run all safety protocols
        for protocol in self.safety_protocols:
            try:
                result = await protocol.check(content, context)
                results.append({
                    "protocol": protocol.get_protocol_name(),
                    "result": result
                })
                
                if not result.passed:
                    overall_passed = False
                    overall_score = min(overall_score, result.score)
                
            except Exception as e:
                logger.error(f"Error in safety protocol {protocol.get_protocol_name()}: {e}")
                overall_passed = False
        
        # Detect security threats
        security_threats = []
        if self.enable_security_monitoring:
            security_threats = await self.security_detector.detect_threats(content, context)
        
        # Generate safety report
        safety_report = {
            "content_hash": hashlib.sha256(content.encode()).hexdigest()[:16],
            "timestamp": datetime.utcnow().isoformat(),
            "overall_passed": overall_passed,
            "overall_score": overall_score,
            "safety_level": self.safety_level.value,
            "protocol_results": results,
            "security_threats": [threat.__dict__ for threat in security_threats],
            "context": context
        }
        
        # Log safety check
        self.safety_logs.append(safety_report)
        
        # Handle violations
        if not overall_passed or security_threats:
            await self._handle_safety_violations(safety_report, security_threats)
        
        return safety_report
    
    async def _handle_safety_violations(self, safety_report: Dict[str, Any], security_threats: List[SecurityThreatReport]):
        """Handle safety violations and security threats"""
        # Log ethical violations
        for result in safety_report.get("protocol_results", []):
            if not result["result"].passed:
                for violation in result["result"].violations:
                    ethical_violation = EthicalViolation(
                        violation_type=EthicalConstraint.NO_HARM,  # Default, should be determined by context
                        description=violation,
                        context=str(safety_report.get("context", {})),
                        detected_by=result["protocol"]
                    )
                    self.ethical_violations.append(ethical_violation)
        
        # Log security incidents
        for threat in security_threats:
            self.security_incidents.append(threat)
        
        # Auto-block threats if enabled
        if self.auto_block_threats and (not safety_report["overall_passed"] or security_threats):
            logger.warning(f"Blocking content due to safety violations: {safety_report['content_hash']}")
            # Implementation would block the content here
    
    async def get_safety_report(self) -> Dict[str, Any]:
        """Get comprehensive safety report"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "safety_level": self.safety_level.value,
            "total_safety_checks": len(self.safety_logs),
            "violations_count": len(self.ethical_violations),
            "security_incidents_count": len(self.security_incidents),
            "recent_violations": [v.__dict__ for v in self.ethical_violations[-10:]],
            "recent_incidents": [i.__dict__ for i in self.security_incidents[-10:]],
            "safety_score": self._calculate_overall_safety_score()
        }
    
    def _calculate_overall_safety_score(self) -> float:
        """Calculate overall safety score"""
        if not self.safety_logs:
            return 1.0
        
        total_score = sum(log.get("overall_score", 0.0) for log in self.safety_logs)
        return total_score / len(self.safety_logs)
    
    async def _load_safety_config(self):
        """Load safety configuration"""
        # Implementation would load from configuration file
        pass
    
    async def _save_safety_logs(self):
        """Save safety logs to database"""
        try:
            async with AsyncSessionLocal() as db:
                for log in self.safety_logs[-100:]:  # Save last 100 logs
                    safety_entry = MemoryStore(
                        agent_id="safety_system",
                        content=json.dumps(log),
                        created_at=datetime.utcnow()
                    )
                    db.add(safety_entry)
                await db.commit()
        except Exception as e:
            logger.error(f"Failed to save safety logs: {e}")
    
    def set_safety_level(self, level: SafetyLevel):
        """Set safety level"""
        self.safety_level = level
        logger.info(f"Set safety level to: {level.value}")
    
    def add_ethical_constraint(self, constraint: EthicalConstraint):
        """Add an ethical constraint"""
        if constraint not in self.ethical_constraints:
            self.ethical_constraints.append(constraint)
            logger.info(f"Added ethical constraint: {constraint.value}")
    
    def remove_ethical_constraint(self, constraint: EthicalConstraint):
        """Remove an ethical constraint"""
        if constraint in self.ethical_constraints:
            self.ethical_constraints.remove(constraint)
            logger.info(f"Removed ethical constraint: {constraint.value}")

# Global safety system instance
safety_system = SafetySystem()

# Convenience functions for external use
async def check_content_safety(content: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Check content for safety violations"""
    return await safety_system.check_content(content, context)

async def get_safety_report() -> Dict[str, Any]:
    """Get safety system report"""
    return await safety_system.get_safety_report()

def set_safety_level(level: SafetyLevel):
    """Set safety level"""
    safety_system.set_safety_level(level)

def add_ethical_constraint(constraint: EthicalConstraint):
    """Add ethical constraint"""
    safety_system.add_ethical_constraint(constraint)

def remove_ethical_constraint(constraint: EthicalConstraint):
    """Remove ethical constraint"""
    safety_system.remove_ethical_constraint(constraint)