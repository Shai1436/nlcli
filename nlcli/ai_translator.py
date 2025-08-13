"""
AI Translator module for converting natural language to OS commands
"""

import json
import os
import platform
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from openai import OpenAI
from typing import Dict, Optional
from .utils import get_platform_info, setup_logging
from .cache_manager import CacheManager

logger = setup_logging()

class AITranslator:
    """Handles natural language to OS command translation using OpenAI with caching and optimization"""
    
    def __init__(self, api_key: Optional[str] = None, enable_cache: bool = True):
        """Initialize AI translator with OpenAI API key and performance optimizations"""
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or provide in config.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.platform_info = get_platform_info()
        
        # Performance optimizations
        self.enable_cache = enable_cache
        self.cache_manager = CacheManager() if enable_cache else None
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Common command patterns for instant recognition
        self.instant_patterns = {
            'ls': ['list files', 'show files', 'list directory', 'dir'],
            'pwd': ['current directory', 'where am i', 'current path', 'show path'],
            'cd': ['change directory', 'go to', 'navigate to'],
            'cat': ['show file', 'read file', 'display file'],
            'mkdir': ['create directory', 'make folder', 'new folder'],
            'rm': ['delete file', 'remove file'],
            'cp': ['copy file', 'duplicate file'],
            'mv': ['move file', 'rename file'],
            'ps': ['show processes', 'list processes', 'running processes'],
            'top': ['system monitor', 'cpu usage', 'memory usage'],
            'df': ['disk usage', 'disk space', 'storage usage'],
            'whoami': ['current user', 'username', 'who am i'],
            'date': ['current time', 'show date', 'what time'],
            'history': ['command history', 'previous commands'],
            'clear': ['clear screen', 'clean terminal', 'clear terminal']
        }
        
    def translate(self, natural_language: str, timeout: float = 5.0) -> Optional[Dict]:
        """
        Translate natural language to OS command with performance optimizations
        
        Args:
            natural_language: User's natural language input
            timeout: Maximum time to wait for API response
            
        Returns:
            Dictionary containing command, explanation, and confidence
        """
        
        try:
            # Step 1: Check for instant pattern matches (sub-millisecond response)
            instant_result = self._check_instant_patterns(natural_language)
            if instant_result:
                logger.debug(f"Instant pattern match for: {natural_language}")
                return instant_result
            
            # Step 2: Check cache (sub-millisecond response)
            if self.cache_manager:
                cached_result = self.cache_manager.get_cached_translation(
                    natural_language, self.platform_info['system']
                )
                if cached_result:
                    logger.debug(f"Cache hit for: {natural_language}")
                    return cached_result
            
            # Step 3: AI translation with timeout (2-5 second response)
            api_result = self._translate_with_ai(natural_language, timeout)
            
            # Cache the result for future use
            if api_result and self.cache_manager:
                self.cache_manager.cache_translation(
                    natural_language, self.platform_info['system'], api_result
                )
            
            return api_result
            
        except Exception as e:
            logger.error(f"AI translation error: {str(e)}")
            return None
    
    def _check_instant_patterns(self, natural_language: str) -> Optional[Dict]:
        """Check for common command patterns for instant translation"""
        
        normalized = natural_language.lower().strip()
        
        # Direct command matching
        for cmd, patterns in self.instant_patterns.items():
            for pattern in patterns:
                if pattern in normalized:
                    return {
                        'command': cmd,
                        'explanation': self._get_command_explanation(cmd),
                        'confidence': 0.98,
                        'cached': False,
                        'instant': True
                    }
        
        return None
    
    def _get_command_explanation(self, cmd: str) -> str:
        """Get explanation for common commands"""
        
        explanations = {
            'ls': 'Lists files and directories in the current directory',
            'pwd': 'Shows the current working directory path',
            'cd': 'Changes the current directory',
            'cat': 'Displays the contents of a file',
            'mkdir': 'Creates a new directory',
            'rm': 'Removes files or directories',
            'cp': 'Copies files or directories',
            'mv': 'Moves or renames files or directories',
            'ps': 'Shows currently running processes',
            'top': 'Displays real-time system processes and resource usage',
            'df': 'Shows disk space usage for mounted filesystems',
            'whoami': 'Shows the current username',
            'date': 'Displays the current date and time',
            'history': 'Shows command history',
            'clear': 'Clears the terminal screen'
        }
        
        return explanations.get(cmd, f'Executes the {cmd} command')
    
    def _translate_with_ai(self, natural_language: str, timeout: float) -> Optional[Dict]:
        """Perform AI translation with timeout"""
        
        def api_call():
            # Create system prompt based on platform
            system_prompt = self._create_system_prompt()
            
            # Create user prompt
            user_prompt = f"""
            Translate this natural language request to an OS command:
            "{natural_language}"
            
            Provide your response as JSON with this exact format:
            {{
                "command": "the actual OS command",
                "explanation": "clear explanation of what the command does",
                "confidence": 0.95,
                "safe": true,
                "reasoning": "why this command is appropriate"
            }}
            """
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using mini for faster response
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,  # Lower temperature for faster, more deterministic responses
                max_tokens=300   # Reduced tokens for faster response
            )
            
            return json.loads(response.choices[0].message.content)
        
        try:
            # Execute API call with timeout
            future = self.executor.submit(api_call)
            result = future.result(timeout=timeout)
            
            # Add performance metadata
            result['cached'] = False
            result['instant'] = False
            
            # Validate required fields
            if not all(key in result for key in ['command', 'explanation']):
                logger.error("AI response missing required fields")
                return None
                
            return result
            
        except TimeoutError:
            logger.warning(f"AI translation timeout after {timeout} seconds")
            return None
        except Exception as e:
            logger.error(f"AI translation error: {str(e)}")
            return None
            
            # Validate required fields
            if not all(key in result for key in ['command', 'explanation']):
                logger.error("AI response missing required fields")
                return None
            
            # Log successful translation
            logger.info(f"Translated '{natural_language}' to '{result['command']}'")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response JSON: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"AI translation error: {str(e)}")
            return None
    
    def _create_system_prompt(self) -> str:
        """Create system prompt based on current platform"""
        
        platform_name = self.platform_info['platform']
        shell_info = self._get_shell_info()
        
        return f"""
        You are an expert system administrator assistant that translates natural language requests into OS commands.
        
        SYSTEM INFORMATION:
        - Platform: {platform_name}
        - Shell: {shell_info}
        - Python Version: {self.platform_info['python_version']}
        
        TRANSLATION RULES:
        1. Always provide commands appropriate for {platform_name}
        2. Use the most common and safe version of commands
        3. Provide clear, detailed explanations
        4. Consider command safety and mark dangerous operations
        5. Use modern command syntax when available
        6. For file operations, use relative paths unless absolute paths are specifically requested
        7. Avoid commands that could cause system damage without explicit user intent
        
        RESPONSE FORMAT:
        Always respond with valid JSON containing:
        - command: The actual OS command to execute
        - explanation: Clear explanation of what the command does
        - confidence: Number between 0 and 1 indicating confidence level
        - safe: Boolean indicating if the command is generally safe
        - reasoning: Brief explanation of your command choice
        
        SAFETY GUIDELINES:
        - Mark commands as unsafe if they:
          * Delete system files or directories
          * Modify system configurations
          * Have potential for data loss
          * Require elevated privileges
          * Affect network security
        - For ambiguous requests, choose the safest interpretation
        - Always explain potential risks in the explanation
        """
    
    def _get_shell_info(self) -> str:
        """Get information about the current shell"""
        
        system = platform.system().lower()
        
        if system == 'windows':
            return 'Command Prompt/PowerShell'
        elif system == 'darwin':
            return 'Bash/Zsh (macOS)'
        else:
            return 'Bash/Sh (Linux/Unix)'
    
    def get_command_suggestions(self, partial_input: str, limit: int = 5) -> list:
        """
        Get command suggestions based on partial input
        
        Args:
            partial_input: Partial natural language input
            limit: Maximum number of suggestions
            
        Returns:
            List of suggested completions
        """
        
        try:
            prompt = f"""
            Given this partial natural language input: "{partial_input}"
            
            Suggest {limit} possible completions that are common OS operations.
            Respond with JSON in this format:
            {{
                "suggestions": [
                    "complete suggestion 1",
                    "complete suggestion 2"
                ]
            }}
            """
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=300
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('suggestions', [])
            
        except Exception as e:
            logger.error(f"Error getting suggestions: {str(e)}")
            return []
