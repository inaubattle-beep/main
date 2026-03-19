#!/usr/bin/env python3
"""
Advanced Code Generation System
Implements sophisticated code generation capabilities for the God AGI Agent.
Supports multiple programming languages, frameworks, and complex software architectures.
"""

import asyncio
import json
import os
import re
import shutil
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Union, Tuple
import ast
import importlib.util

from core.llm import llm_client
from core.logger import logger
from core.safety import safety_system
from memory.database import AsyncSessionLocal
from memory.models import Task, TaskState, Agent, MemoryStore

class ProgrammingLanguage(Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    C_SHARP = "csharp"
    GO = "go"
    RUST = "rust"
    C_PLUS_PLUS = "cpp"
    C = "c"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    PHP = "php"
    RUBY = "ruby"
    R = "r"
    JULIA = "julia"
    SCALA = "scala"
    HTML = "html"
    CSS = "css"
    SQL = "sql"

class FrameworkType(Enum):
    """Supported framework types"""
    WEB = "web"
    MOBILE = "mobile"
    DESKTOP = "desktop"
    GAME = "game"
    DATA_SCIENCE = "data_science"
    MACHINE_LEARNING = "machine_learning"
    DEVOPS = "devops"
    CLOUD = "cloud"
    EMBEDDED = "embedded"
    SYSTEMS = "systems"

@dataclass
class CodeTemplate:
    """Code template for generation"""
    template_id: str
    language: ProgrammingLanguage
    framework: Optional[str]
    description: str
    template_content: str
    dependencies: List[str] = field(default_factory=list)
    parameters: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class GeneratedCode:
    """Generated code result"""
    generation_id: str
    language: ProgrammingLanguage
    framework: Optional[str]
    files: Dict[str, str]  # filename -> content
    dependencies: Dict[str, List[str]]  # language -> dependencies
    metadata: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.utcnow)
    quality_score: float = 0.0
    security_score: float = 0.0

class CodeGenerator(ABC):
    """Abstract base class for code generators"""
    
    @abstractmethod
    async def generate(self, requirements: str, language: ProgrammingLanguage, 
                      framework: Optional[str] = None, **kwargs) -> GeneratedCode:
        """Generate code based on requirements"""
        pass
    
    @abstractmethod
    def supports_language(self, language: ProgrammingLanguage) -> bool:
        """Check if generator supports the language"""
        pass

class PythonCodeGenerator(CodeGenerator):
    """Python code generator with advanced capabilities"""
    
    def __init__(self):
        self.templates = self._load_python_templates()
    
    def supports_language(self, language: ProgrammingLanguage) -> bool:
        return language == ProgrammingLanguage.PYTHON
    
    async def generate(self, requirements: str, language: ProgrammingLanguage, 
                      framework: Optional[str] = None, **kwargs) -> GeneratedCode:
        """Generate Python code"""
        try:
            # Analyze requirements
            analysis = await self._analyze_requirements(requirements, framework)
            
            # Generate main code
            main_code = await self._generate_main_code(requirements, analysis, framework)
            
            # Generate supporting files
            supporting_files = await self._generate_supporting_files(analysis, framework)
            
            # Generate configuration files
            config_files = await self._generate_config_files(analysis, framework)
            
            # Generate documentation
            docs = await self._generate_documentation(requirements, analysis, framework)
            
            # Combine all files
            all_files = {**main_code, **supporting_files, **config_files, **docs}
            
            # Calculate quality and security scores
            quality_score = await self._calculate_quality_score(all_files)
            security_score = await self._calculate_security_score(all_files)
            
            # Create generated code object
            generated_code = GeneratedCode(
                generation_id=f"py_{int(datetime.utcnow().timestamp())}_{hash(requirements) % 10000}",
                language=language,
                framework=framework,
                files=all_files,
                dependencies=analysis.get("dependencies", {}),
                metadata={
                    "analysis": analysis,
                    "framework": framework,
                    "complexity": analysis.get("complexity", "medium")
                },
                quality_score=quality_score,
                security_score=security_score
            )
            
            # Store in memory
            await self._store_generated_code(generated_code)
            
            return generated_code
            
        except Exception as e:
            logger.error(f"Python code generation failed: {e}")
            raise
    
    async def _analyze_requirements(self, requirements: str, framework: Optional[str]) -> Dict[str, Any]:
        """Analyze requirements to determine structure and dependencies"""
        prompt = f"""
        Analyze these requirements for a Python project:
        
        Requirements: {requirements}
        Framework: {framework or 'standard libraries'}
        
        Provide analysis with:
        1. Project type (web app, CLI tool, library, etc.)
        2. Required dependencies and packages
        3. Project structure (modules, classes, functions needed)
        4. Complexity level (simple, medium, complex)
        5. Testing requirements
        6. Documentation needs
        
        Return as JSON with keys: project_type, dependencies, structure, complexity, testing, documentation
        """
        
        try:
            response = await llm_client.generate_response(prompt)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Requirements analysis failed: {e}")
            return {
                "project_type": "general",
                "dependencies": {"python": ["os", "sys", "json"]},
                "structure": {"main.py": "main entry point"},
                "complexity": "simple",
                "testing": False,
                "documentation": False
            }
    
    async def _generate_main_code(self, requirements: str, analysis: Dict[str, Any], 
                                framework: Optional[str]) -> Dict[str, str]:
        """Generate main application code"""
        project_type = analysis.get("project_type", "general")
        
        if project_type == "web app":
            return await self._generate_web_app(requirements, framework)
        elif project_type == "cli tool":
            return await self._generate_cli_tool(requirements)
        elif project_type == "library":
            return await self._generate_library(requirements)
        else:
            return await self._generate_general_code(requirements, analysis)
    
    async def _generate_web_app(self, requirements: str, framework: Optional[str]) -> Dict[str, str]:
        """Generate web application"""
        if framework == "flask":
            return await self._generate_flask_app(requirements)
        elif framework == "django":
            return await self._generate_django_app(requirements)
        elif framework == "fastapi":
            return await self._generate_fastapi_app(requirements)
        else:
            return await self._generate_basic_web_app(requirements)
    
    async def _generate_flask_app(self, requirements: str) -> Dict[str, str]:
        """Generate Flask web application"""
        prompt = f"""
        Generate a complete Flask web application based on these requirements:
        
        Requirements: {requirements}
        
        Include:
        1. app.py - Main Flask application with routes
        2. models.py - Data models if needed
        3. templates/ directory with base template
        4. static/ directory structure
        
        Return as JSON with file paths as keys and file contents as values.
        """
        
        response = await llm_client.generate_response(prompt)
        return json.loads(response)
    
    async def _generate_django_app(self, requirements: str) -> Dict[str, str]:
        """Generate Django web application"""
        prompt = f"""
        Generate a complete Django web application based on these requirements:
        
        Requirements: {requirements}
        
        Include:
        1. manage.py
        2. settings.py
        3. urls.py
        4. views.py
        5. models.py
        6. templates/ directory
        7. static/ directory
        
        Return as JSON with file paths as keys and file contents as values.
        """
        
        response = await llm_client.generate_response(prompt)
        return json.loads(response)
    
    async def _generate_fastapi_app(self, requirements: str) -> Dict[str, str]:
        """Generate FastAPI web application"""
        prompt = f"""
        Generate a complete FastAPI web application based on these requirements:
        
        Requirements: {requirements}
        
        Include:
        1. main.py - FastAPI application
        2. models.py - Pydantic models
        3. routers/ directory with API endpoints
        4. dependencies.py - Dependency injection
        
        Return as JSON with file paths as keys and file contents as values.
        """
        
        response = await llm_client.generate_response(prompt)
        return json.loads(response)
    
    async def _generate_cli_tool(self, requirements: str) -> Dict[str, str]:
        """Generate CLI tool"""
        prompt = f"""
        Generate a complete CLI tool based on these requirements:
        
        Requirements: {requirements}
        
        Include:
        1. main.py - CLI entry point with argparse or click
        2. commands/ directory with command implementations
        3. config.py - Configuration handling
        4. utils.py - Utility functions
        
        Return as JSON with file paths as keys and file contents as values.
        """
        
        response = await llm_client.generate_response(prompt)
        return json.loads(response)
    
    async def _generate_library(self, requirements: str) -> Dict[str, str]:
        """Generate Python library"""
        prompt = f"""
        Generate a complete Python library based on these requirements:
        
        Requirements: {requirements}
        
        Include:
        1. __init__.py
        2. main module with core functionality
        3. utils module
        4. exceptions module
        5. tests/ directory structure
        
        Return as JSON with file paths as keys and file contents as values.
        """
        
        response = await llm_client.generate_response(prompt)
        return json.loads(response)
    
    async def _generate_general_code(self, requirements: str, analysis: Dict[str, Any]) -> Dict[str, str]:
        """Generate general purpose Python code"""
        prompt = f"""
        Generate Python code based on these requirements:
        
        Requirements: {requirements}
        Analysis: {json.dumps(analysis)}
        
        Create appropriate Python files based on the analysis.
        
        Return as JSON with file paths as keys and file contents as values.
        """
        
        response = await llm_client.generate_response(prompt)
        return json.loads(response)
    
    async def _generate_supporting_files(self, analysis: Dict[str, Any], 
                                       framework: Optional[str]) -> Dict[str, str]:
        """Generate supporting files like tests, utilities, etc."""
        files = {}
        
        # Generate tests if required
        if analysis.get("testing", False):
            files["tests/test_main.py"] = await self._generate_tests(analysis, framework)
        
        # Generate utilities
        files["utils/helpers.py"] = await self._generate_utils()
        
        # Generate configuration
        files["config.py"] = await self._generate_config()
        
        return files
    
    async def _generate_tests(self, analysis: Dict[str, Any], framework: Optional[str]) -> str:
        """Generate test files"""
        prompt = f"""
        Generate comprehensive tests for a Python project:
        
        Analysis: {json.dumps(analysis)}
        Framework: {framework}
        
        Use pytest framework. Include:
        1. Unit tests for main functionality
        2. Integration tests if applicable
        3. Mock objects where needed
        
        Return the test file content.
        """
        
        return await llm_client.generate_response(prompt)
    
    async def _generate_utils(self) -> str:
        """Generate utility functions"""
        return '''
"""
Utility functions for the application.
"""

import os
import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Config file {config_path} not found, using defaults")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing config file {config_path}: {e}")
        return {}


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """Safely divide two numbers."""
    try:
        return a / b
    except ZeroDivisionError:
        return default


def format_bytes(size: int) -> str:
    """Format bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"
'''

    async def _generate_config(self) -> str:
        """Generate configuration file"""
        return '''
"""
Application configuration.
"""

import os
from typing import Dict, Any

# Environment-based configuration
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")

# API configuration
API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# Application settings
APP_NAME = "Generated Application"
VERSION = "1.0.0"

def get_config() -> Dict[str, Any]:
    """Get current configuration."""
    return {
        "debug": DEBUG,
        "log_level": LOG_LEVEL,
        "database_url": DATABASE_URL,
        "api_host": API_HOST,
        "api_port": API_PORT,
        "secret_key": SECRET_KEY,
        "app_name": APP_NAME,
        "version": VERSION
    }
'''

    async def _generate_config_files(self, analysis: Dict[str, Any], 
                                   framework: Optional[str]) -> Dict[str, str]:
        """Generate configuration files"""
        files = {}
        
        # requirements.txt
        dependencies = analysis.get("dependencies", {}).get("python", [])
        files["requirements.txt"] = self._generate_requirements(dependencies, framework)
        
        # setup.py or pyproject.toml
        if framework in ["django", "flask", "fastapi"]:
            files["setup.py"] = self._generate_setup_py(analysis, framework)
        else:
            files["pyproject.toml"] = self._generate_pyproject_toml(analysis, framework)
        
        # .gitignore
        files[".gitignore"] = self._generate_gitignore()
        
        return files
    
    def _generate_requirements(self, dependencies: List[str], framework: Optional[str]) -> str:
        """Generate requirements.txt"""
        base_requirements = [
            "python-dotenv>=0.19.0",
            "requests>=2.28.0",
        ]
        
        if framework == "flask":
            base_requirements.extend([
                "Flask>=2.2.0",
                "Werkzeug>=2.2.0",
            ])
        elif framework == "django":
            base_requirements.extend([
                "Django>=4.0.0",
                "django-cors-headers>=3.13.0",
            ])
        elif framework == "fastapi":
            base_requirements.extend([
                "fastapi>=0.85.0",
                "uvicorn[standard]>=0.18.0",
                "pydantic>=1.10.0",
            ])
        
        # Add specific dependencies
        all_requirements = base_requirements + dependencies
        
        return "\n".join(sorted(set(all_requirements)))
    
    def _generate_setup_py(self, analysis: Dict[str, Any], framework: Optional[str]) -> str:
        """Generate setup.py"""
        project_name = analysis.get("project_type", "generated_app")
        
        return f'''
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="{project_name}",
    version="1.0.0",
    author="Generated by God AGI",
    author_email="noreply@example.com",
    description="Generated Python application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={{
        "console_scripts": [
            "{project_name}={project_name.replace('-', '_')}.main:main",
        ],
    }},
)
'''
    
    def _generate_pyproject_toml(self, analysis: Dict[str, Any], framework: Optional[str]) -> str:
        """Generate pyproject.toml"""
        project_name = analysis.get("project_type", "generated_app")
        
        return f'''
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{project_name}"
version = "1.0.0"
description = "Generated Python application"
readme = "README.md"
authors = [{{name = "Generated by God AGI", email = "noreply@example.com"}}]
license = {{text = "MIT"}}
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
requires-python = ">=3.8"

[project.urls]
Homepage = "https://github.com/example/{project_name}"
Repository = "https://github.com/example/{project_name}"

[tool.setuptools.packages.find]
where = ["."]
'''
    
    def _generate_gitignore(self) -> str:
        """Generate .gitignore"""
        return '''
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.local
.env.*.local

# Logs
*.log
logs/

# Testing
.pytest_cache/
.coverage
htmlcov/
.nox/

# Virtual environments
venv/
env/
ENV/
'''
    
    async def _generate_documentation(self, requirements: str, analysis: Dict[str, Any], 
                                    framework: Optional[str]) -> Dict[str, str]:
        """Generate documentation"""
        files = {}
        
        # README.md
        files["README.md"] = await self._generate_readme(requirements, analysis, framework)
        
        # API documentation if web framework
        if framework in ["flask", "django", "fastapi"]:
            files["docs/api.md"] = await self._generate_api_docs(analysis, framework)
        
        return files
    
    async def _generate_readme(self, requirements: str, analysis: Dict[str, Any], 
                             framework: Optional[str]) -> str:
        """Generate README.md"""
        prompt = f"""
        Generate a comprehensive README.md for a Python project:
        
        Requirements: {requirements}
        Analysis: {json.dumps(analysis)}
        Framework: {framework}
        
        Include:
        1. Project title and description
        2. Installation instructions
        3. Usage examples
        4. Configuration options
        5. Contributing guidelines
        6. License information
        
        Return the README content in Markdown format.
        """
        
        return await llm_client.generate_response(prompt)
    
    async def _generate_api_docs(self, analysis: Dict[str, Any], framework: Optional[str]) -> str:
        """Generate API documentation"""
        prompt = f"""
        Generate API documentation for a web framework project:
        
        Analysis: {json.dumps(analysis)}
        Framework: {framework}
        
        Include:
        1. API endpoints description
        2. Request/response examples
        3. Authentication information
        4. Error handling
        
        Return the documentation content in Markdown format.
        """
        
        return await llm_client.generate_response(prompt)
    
    async def _calculate_quality_score(self, files: Dict[str, str]) -> float:
        """Calculate code quality score"""
        total_score = 0.0
        file_count = 0
        
        for filename, content in files.items():
            if filename.endswith('.py'):
                score = self._analyze_python_quality(content)
                total_score += score
                file_count += 1
        
        return total_score / file_count if file_count > 0 else 1.0
    
    def _analyze_python_quality(self, code: str) -> float:
        """Analyze Python code quality"""
        score = 1.0
        
        # Check for docstrings
        if '"""' not in code and "'''" not in code:
            score -= 0.1
        
        # Check for type hints
        if '->' not in code and ': ' not in code:
            score -= 0.1
        
        # Check for imports organization
        if not code.startswith('import') and not code.startswith('from'):
            score -= 0.05
        
        # Check for error handling
        if 'try:' not in code and 'except' not in code:
            score -= 0.05
        
        # Check for comments
        comment_lines = len([line for line in code.split('\n') if line.strip().startswith('#')])
        if comment_lines < 5:
            score -= 0.05
        
        return max(0.0, min(1.0, score))
    
    async def _calculate_security_score(self, files: Dict[str, str]) -> float:
        """Calculate security score"""
        score = 1.0
        
        for filename, content in files.items():
            # Check for hardcoded secrets
            if re.search(r'password\s*=\s*["\'][^"\']{3,}["\']', content, re.IGNORECASE):
                score -= 0.2
            
            # Check for SQL injection vulnerabilities
            if re.search(r'execute\s*\(\s*["\'].*%.*["\']', content):
                score -= 0.3
            
            # Check for unsafe eval/exec
            if 'eval(' in content or 'exec(' in content:
                score -= 0.4
        
        return max(0.0, min(1.0, score))
    
    async def _store_generated_code(self, generated_code: GeneratedCode):
        """Store generated code in database"""
        try:
            async with AsyncSessionLocal() as db:
                memory_entry = MemoryStore(
                    agent_id="code_generator",
                    content=json.dumps({
                        "generation_id": generated_code.generation_id,
                        "language": generated_code.language.value,
                        "framework": generated_code.framework,
                        "files_count": len(generated_code.files),
                        "quality_score": generated_code.quality_score,
                        "security_score": generated_code.security_score,
                        "metadata": generated_code.metadata
                    }),
                    created_at=generated_code.generated_at
                )
                db.add(memory_entry)
                await db.commit()
        except Exception as e:
            logger.error(f"Failed to store generated code: {e}")
    
    def _load_python_templates(self) -> Dict[str, CodeTemplate]:
        """Load Python code templates"""
        return {
            "flask_api": CodeTemplate(
                template_id="flask_api",
                language=ProgrammingLanguage.PYTHON,
                framework="flask",
                description="Flask REST API template",
                template_content=self._get_flask_api_template(),
                dependencies=["flask", "flask-cors", "flask-restful"],
                parameters=["api_name", "endpoints"]
            ),
            "django_app": CodeTemplate(
                template_id="django_app",
                language=ProgrammingLanguage.PYTHON,
                framework="django",
                description="Django web application template",
                template_content=self._get_django_app_template(),
                dependencies=["django", "django-cors-headers"],
                parameters=["app_name", "models"]
            ),
            "cli_tool": CodeTemplate(
                template_id="cli_tool",
                language=ProgrammingLanguage.PYTHON,
                framework=None,
                description="CLI tool template",
                template_content=self._get_cli_tool_template(),
                dependencies=["click", "rich"],
                parameters=["tool_name", "commands"]
            )
        }
    
    def _get_flask_api_template(self) -> str:
        """Get Flask API template"""
        return '''
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restful import Api, Resource
import os
import logging

app = Flask(__name__)
CORS(app)
api = Api(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class {{api_name}}API(Resource):
    def get(self):
        """Get API status"""
        return {"status": "running", "api": "{{api_name}}"}
    
    def post(self):
        """Process data"""
        data = request.get_json()
        # Process data here
        return {"message": "Data processed", "data": data}

api.add_resource({{api_name}}API, '/api/{{api_name.lower()}}')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
'''
    
    def _get_django_app_template(self) -> str:
        """Get Django app template"""
        return '''
# settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    '{{app_name}}',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = '{{app_name}}.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = '{{app_name}}.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
'''
    
    def _get_cli_tool_template(self) -> str:
        """Get CLI tool template"""
        return '''
import click
from rich.console import Console
from rich.progress import Progress
import logging

console = Console()

@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, verbose):
    """{{tool_name}} - A powerful CLI tool"""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    
    # Setup logging
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format='%(levelname)s: %(message)s')

@cli.command()
@click.argument('name')
@click.option('--count', '-c', default=1, help='Number of greetings')
@click.pass_context
def hello(ctx, name, count):
    """Say hello to NAME"""
    verbose = ctx.obj['verbose']
    
    with Progress() as progress:
        task = progress.add_task(f"[cyan]Processing...", total=count)
        
        for i in range(count):
            if verbose:
                logging.info(f"Processing greeting {i+1}")
            
            console.print(f"Hello, {name}! ({i+1}/{count})")
            progress.update(task, advance=1)

@cli.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@click.pass_context
def process(ctx, files):
    """Process FILES"""
    verbose = ctx.obj['verbose']
    
    if not files:
        console.print("[yellow]No files specified[/yellow]")
        return
    
    console.print(f"Processing {len(files)} file(s)...")
    
    with Progress() as progress:
        task = progress.add_task("[green]Processing files...", total=len(files))
        
        for file_path in files:
            if verbose:
                logging.info(f"Processing file: {file_path}")
            
            # Process file here
            console.print(f"✓ Processed: {file_path}")
            progress.update(task, advance=1)

if __name__ == '__main__':
    cli()
'''

class JavaScriptCodeGenerator(CodeGenerator):
    """JavaScript/TypeScript code generator"""
    
    def supports_language(self, language: ProgrammingLanguage) -> bool:
        return language in [ProgrammingLanguage.JAVASCRIPT, ProgrammingLanguage.TYPESCRIPT]
    
    async def generate(self, requirements: str, language: ProgrammingLanguage, 
                      framework: Optional[str] = None, **kwargs) -> GeneratedCode:
        """Generate JavaScript/TypeScript code"""
        # Implementation similar to Python generator but for JS/TS
        # This would include React, Vue, Angular, Node.js, etc.
        pass

class CodeGenerationSystem:
    """Main code generation system"""
    
    def __init__(self):
        self.generators: List[CodeGenerator] = [
            PythonCodeGenerator(),
            JavaScriptCodeGenerator(),
        ]
        self.is_running = False
    
    async def start(self):
        """Start the code generation system"""
        logger.info("Starting Code Generation System...")
        self.is_running = True
        logger.info("Code Generation System started successfully")
    
    async def stop(self):
        """Stop the code generation system"""
        logger.info("Stopping Code Generation System...")
        self.is_running = False
        logger.info("Code Generation System stopped")
    
    async def generate_code(self, requirements: str, language: ProgrammingLanguage, 
                           framework: Optional[str] = None, **kwargs) -> GeneratedCode:
        """Generate code based on requirements"""
        if not self.is_running:
            raise Exception("Code generation system not running")
        
        # Find appropriate generator
        generator = None
        for gen in self.generators:
            if gen.supports_language(language):
                generator = gen
                break
        
        if not generator:
            raise Exception(f"No generator available for language: {language}")
        
        # Perform safety check
        safety_result = await safety_system.check_content(requirements, {
            "language": language.value,
            "framework": framework,
            "type": "code_generation"
        })
        
        if not safety_result["overall_passed"]:
            raise Exception("Code generation blocked by safety system")
        
        # Generate code
        generated_code = await generator.generate(requirements, language, framework, **kwargs)
        
        # Validate generated code
        validation_result = await self._validate_generated_code(generated_code)
        
        if not validation_result["valid"]:
            logger.warning(f"Generated code validation failed: {validation_result['issues']}")
        
        return generated_code
    
    async def _validate_generated_code(self, generated_code: GeneratedCode) -> Dict[str, Any]:
        """Validate generated code"""
        issues = []
        
        # Check for syntax errors in Python files
        if generated_code.language == ProgrammingLanguage.PYTHON:
            for filename, content in generated_code.files.items():
                if filename.endswith('.py'):
                    try:
                        ast.parse(content)
                    except SyntaxError as e:
                        issues.append(f"Syntax error in {filename}: {e}")
        
        # Check quality scores
        if generated_code.quality_score < 0.5:
            issues.append(f"Low quality score: {generated_code.quality_score}")
        
        if generated_code.security_score < 0.5:
            issues.append(f"Low security score: {generated_code.security_score}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "quality_score": generated_code.quality_score,
            "security_score": generated_code.security_score
        }
    
    async def save_generated_code(self, generated_code: GeneratedCode, output_dir: str) -> bool:
        """Save generated code to filesystem"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Save each file
            for filename, content in generated_code.files.items():
                file_path = output_path / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            logger.info(f"Generated code saved to: {output_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save generated code: {e}")
            return False

# Global code generation system instance
code_generation_system = CodeGenerationSystem()

# Convenience functions for external use
async def generate_code(requirements: str, language: ProgrammingLanguage, 
                       framework: Optional[str] = None, **kwargs) -> GeneratedCode:
    """Generate code based on requirements"""
    return await code_generation_system.generate_code(requirements, language, framework, **kwargs)

async def save_generated_code(generated_code: GeneratedCode, output_dir: str) -> bool:
    """Save generated code to filesystem"""
    return await code_generation_system.save_generated_code(generated_code, output_dir)