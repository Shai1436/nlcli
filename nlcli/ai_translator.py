"""
AI Translator module for converting natural language to OS commands
"""

import json
import os
import platform
from openai import OpenAI
from typing import Dict, Optional
from .utils import get_platform_info, setup_logging

logger = setup_logging()

class AITranslator:
    """Handles natural language to OS command translation using OpenAI"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize AI translator with OpenAI API key"""
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or provide in config.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.platform_info = get_platform_info()
        
    def translate(self, natural_language: str) -> Optional[Dict]:
        """
        Translate natural language to OS command
        
        Args:
            natural_language: User's natural language input
            
        Returns:
            Dictionary containing command, explanation, and confidence
        """
        
        try:
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
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=500
            )
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            
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
