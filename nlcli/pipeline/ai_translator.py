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
from rich.console import Console
from rich.prompt import Prompt
from ..utils.utils import get_platform_info, setup_logging
from ..storage.cache_manager import CacheManager

logger = setup_logging()
console = Console()

class AITranslator:
    """Handles natural language to OS command translation using OpenAI with caching and optimization"""
    
    def __init__(self, api_key: Optional[str] = None, enable_cache: bool = True):
        """Initialize AI translator with OpenAI API key and performance optimizations"""
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        self._api_key_prompted = False
        
        # Only initialize OpenAI client if API key is available
        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self.client = None
        
        # Performance optimizations
        self.enable_cache = enable_cache
        self.cache_manager = CacheManager() if enable_cache else None
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Persistent context system
        self.persistent_context = None
        self.persistent_system_prompt = None
        self.last_context_hash = None
        
        # Initialize Pipeline Components (Level 1-4) - Clean Architecture
        from .shell_adapter import ShellAdapter
        from .command_filter import CommandFilter 
        from .pattern_engine import PatternEngine
        from .fuzzy_engine import AdvancedFuzzyEngine
        from ..ui.command_selector import CommandSelector
        
        # Level 1: Context (owns ALL context managers)
        self.shell_adapter = ShellAdapter()
        
        # Level 2,4: Processing components (Pattern Engine removed - handled by Semantic Matcher)
        self.command_filter = CommandFilter()
        self.fuzzy_engine = AdvancedFuzzyEngine()
        self.command_selector = CommandSelector()
        
        # Load persistent context from shell adapter
        self._load_persistent_context()
        
        # REMOVED: Hard-coded instant patterns - defeats the purpose of AI intelligence
        # Let semantic understanding and AI translation handle all natural language patterns
        self.instant_patterns = {}
        
    def translate(self, natural_language: str, context: Optional[Dict] = None, timeout: float = 8.0) -> Optional[Dict]:
        """
        Translate natural language to OS command using provided context
        
        Args:
            natural_language: User's natural language input
            context: Platform/shell context from shell_adapter (optional for backwards compatibility)
            timeout: Maximum time to wait for API response
            
        Returns:
            Dictionary containing command, explanation, and confidence
        """
        
        try:
            # STREAMLINED PIPELINE FLOW (Levels 1,2,4,5,6 - Skipping Pattern Engine)
            
            # Level 1: Shell Adapter - Get context
            context = self.shell_adapter.get_pipeline_metadata(natural_language)
            logger.debug(f"Level 1 (Shell Adapter): Context generated")
            
            # Level 2: Command Filter - Check direct commands
            level2_result = self.command_filter.get_pipeline_metadata(natural_language)
            if level2_result:
                logger.debug(f"Level 2 (Command Filter): Direct match found")
                return {**level2_result, 'cached': False, 'instant': True}
            
            # Level 4: Fuzzy Engine - Fuzzy matching + typo correction
            level4_result = self.fuzzy_engine.get_pipeline_metadata(natural_language, context)
            if level4_result:
                logger.debug(f"Level 4 (Fuzzy Engine): Fuzzy match found")
                return {**level4_result, 'cached': False, 'instant': True}
            
            # Level 5: Semantic Matcher - Intelligent Intent Classification
            try:
                from .semantic_matcher import SemanticMatcher
                if not hasattr(self, '_semantic_matcher'):
                    self._semantic_matcher = SemanticMatcher()
                
                level5_result = self._semantic_matcher.get_pipeline_metadata(natural_language, context)
                if level5_result:
                    logger.debug(f"Level 5 (Semantic Matcher): Intent classified")
                    return {**level5_result, 'cached': False, 'instant': True}
            except ImportError:
                logger.debug("Semantic Matcher not available")
            except Exception as e:
                logger.warning(f"Semantic Matcher error: {e}")
            
            # Level 6: AI Translation - OpenAI fallback
            logger.debug(f"Level 6 (AI Translation): Using OpenAI fallback")
            api_result = self._translate_with_ai(natural_language, timeout, context)
            
            # Cache the result for future use
            if api_result and self.cache_manager:
                platform_key = context.get('platform', 'unknown')
                self.cache_manager.cache_translation(
                    natural_language, platform_key, api_result
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
            # File and Directory Operations
            'ls': 'Lists files and directories in the current directory',
            'ls -la': 'Lists all files including hidden ones with detailed information',
            'ls -lh': 'Lists files with human-readable file sizes',
            'pwd': 'Shows the current working directory path',
            'cd': 'Changes the current directory',
            'cd ..': 'Changes to the parent directory',
            'cd ~': 'Changes to the home directory',
            'cat': 'Displays the contents of a file',
            'head': 'Shows the first 10 lines of a file',
            'tail': 'Shows the last 10 lines of a file',
            'tail -f': 'Continuously monitors and displays new lines added to a file',
            'less': 'Views file content page by page with navigation',
            'more': 'Views file content one screen at a time',
            'mkdir': 'Creates a new directory',
            'mkdir -p': 'Creates directories including parent directories as needed',
            'rmdir': 'Removes empty directories',
            'rm': 'Removes files or directories',
            'rm -rf': 'Forcefully removes files and directories recursively',
            'cp': 'Copies files or directories',
            'cp -r': 'Copies directories and their contents recursively',
            'mv': 'Moves or renames files or directories',
            'touch': 'Creates a new empty file or updates file timestamp',
            'find .': 'Searches for files and directories in current location',
            'locate': 'Finds files by name using system database',
            'which': 'Shows the location of a command',
            'ln -s': 'Creates a symbolic link to a file or directory',
            
            # File Content and Text Processing
            'grep': 'Searches for text patterns within files',
            'sort': 'Sorts lines in a file alphabetically',
            'uniq': 'Filters out duplicate lines from sorted input',
            'wc': 'Counts words, lines, and characters in files',
            'wc -l': 'Counts the number of lines in a file',
            'diff': 'Compares two files and shows differences',
            'cut': 'Extracts specific columns or fields from text',
            'awk': 'Processes and manipulates text data',
            'sed': 'Edits text using stream editing commands',
            
            # System Information and Monitoring
            'ps': 'Shows currently running processes',
            'ps aux': 'Shows detailed information about all running processes',
            'top': 'Displays real-time system processes and resource usage',
            'htop': 'Interactive process viewer with enhanced features',
            'df': 'Shows disk space usage for mounted filesystems',
            'df -h': 'Shows disk space usage in human-readable format',
            'du': 'Shows directory space usage',
            'du -sh': 'Shows total directory size in human-readable format',
            'free': 'Displays memory usage information',
            'free -h': 'Shows memory usage in human-readable format',
            'uname': 'Shows system information',
            'uname -a': 'Shows detailed system information including kernel version',
            'uptime': 'Shows how long the system has been running',
            'whoami': 'Shows the current username',
            'id': 'Shows user and group IDs',
            'w': 'Shows who is logged in and what they are doing',
            'last': 'Shows recent login history',
            
            # Network and Connectivity
            'ping': 'Tests network connectivity to a host',
            'wget': 'Downloads files from the internet',
            'curl': 'Transfers data from or to servers',
            'netstat': 'Shows network connections and statistics',
            'ss': 'Shows socket statistics and connections',
            'ifconfig': 'Displays and configures network interfaces',
            'ip addr': 'Shows IP addresses and network interface information',
            
            # Archives and Compression
            'tar -xzf': 'Extracts compressed tar archive files',
            'tar -czf': 'Creates compressed tar archive files',
            'zip': 'Creates compressed zip archive files',
            'unzip': 'Extracts files from zip archives',
            'gzip': 'Compresses files using gzip compression',
            'gunzip': 'Decompresses gzip compressed files',
            
            # File Permissions and Ownership
            'chmod': 'Changes file permissions',
            'chmod +x': 'Makes a file executable',
            'chown': 'Changes file ownership',
            'chgrp': 'Changes file group ownership',
            
            # Environment and Variables
            'env': 'Shows environment variables',
            'export': 'Sets environment variables',
            'echo': 'Displays text or variable values',
            'date': 'Displays the current date and time',
            'cal': 'Shows a calendar',
            'history': 'Shows command history',
            'alias': 'Shows or creates command aliases',
            
            # Terminal and Session
            'clear': 'Clears the terminal screen',
            'reset': 'Resets the terminal to default state',
            'exit': 'Exits the current shell or terminal',
            'logout': 'Logs out of the current session',
            'screen': 'Starts a new terminal session',
            'tmux': 'Starts terminal multiplexer for multiple sessions',
            
            # Package Management (Linux)
            'sudo apt update': 'Updates the package list from repositories',
            'sudo apt upgrade': 'Upgrades all installed packages to latest versions',
            'sudo apt install': 'Installs new software packages',
            'apt search': 'Searches for available packages',
            'dpkg -l': 'Lists all installed packages',
            
            # Git Commands
            'git status': 'Shows the status of files in the git repository',
            'git log': 'Shows the commit history',
            'git diff': 'Shows changes between commits or working directory',
            'git add .': 'Stages all changes for the next commit',
            'git commit': 'Creates a new commit with staged changes',
            'git push': 'Uploads commits to remote repository',
            'git pull': 'Downloads and merges changes from remote repository',
            'git clone': 'Creates a local copy of a remote repository'
        }
        
        return explanations.get(cmd, f'Executes the {cmd} command')
    
    def _load_persistent_context(self):
        """Load persistent context from ShellAdapter - called once at initialization"""
        try:
            # Get comprehensive context from shell adapter
            self.persistent_context = self.shell_adapter.get_enhanced_context()
            
            # Create hash of context for change detection
            import hashlib
            # Convert any unhashable types to strings for JSON serialization
            hashable_context = self._make_hashable(self.persistent_context)
            context_str = json.dumps(hashable_context, sort_keys=True)
            self.last_context_hash = hashlib.md5(context_str.encode()).hexdigest()
            
            # Create persistent system prompt with all context
            self._create_persistent_system_prompt()
            
            logger.debug(f"Persistent context loaded: platform={self.persistent_context.get('platform')}, "
                        f"git_repo={self.persistent_context.get('git', {}).get('is_git_repo')}, "
                        f"project_type={self.persistent_context.get('environment', {}).get('project_type')}")
            
        except Exception as e:
            logger.warning(f"Failed to load persistent context: {e}")
            self.persistent_context = {}
            self._create_persistent_system_prompt()
    
    def _make_hashable(self, obj):
        """Convert unhashable types to hashable ones for JSON serialization"""
        if isinstance(obj, dict):
            return {k: self._make_hashable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_hashable(item) for item in obj]
        elif isinstance(obj, set):
            return list(obj)  # Convert set to list
        elif hasattr(obj, '__dict__'):
            return str(obj)  # Convert objects to string representation
        else:
            return obj
    
    def _create_persistent_system_prompt(self):
        """Create comprehensive system prompt with all persistent context"""
        
        if not self.persistent_context:
            # Fallback system prompt
            self.persistent_system_prompt = """
            You are an expert system administrator assistant that translates natural language requests into OS commands.
            Provide clear, safe, and appropriate commands for the user's system.
            """
            return
        
        # Extract context information
        platform = self.persistent_context.get('platform', 'unknown')
        shell = self.persistent_context.get('shell', 'unknown')
        available_commands = self.persistent_context.get('available_commands', [])
        git_context = self.persistent_context.get('git', {})
        env_context = self.persistent_context.get('environment', {})
        shell_features = self.persistent_context.get('shell_features', [])
        
        # Build rich context-aware system prompt with enhanced natural language understanding
        self.persistent_system_prompt = f"""
        You are an expert system administrator assistant that translates natural language requests into OS commands.
        You have persistent awareness of the user's environment and should leverage this context for intelligent command translation.
        
        CURRENT SYSTEM CONTEXT:
        - Platform: {platform.title()} 
        - Shell: {shell}
        - Available Commands: {len(available_commands)} commands available
        - Shell Features: {', '.join(shell_features)}
        - Current Working Directory: {env_context.get('project_root', '/unknown')}
        
        GIT REPOSITORY CONTEXT:
        - Git Repository: {'Yes' if git_context.get('is_git_repo') else 'No'}
        - Current Branch: {git_context.get('current_branch', 'N/A')}
        - Has Changes: {'Yes' if git_context.get('has_staged_changes') or git_context.get('has_unstaged_changes') else 'No'}
        - Repository Root: {git_context.get('repository_root', 'N/A')}
        
        PROJECT ENVIRONMENT:
        - Project Type: {env_context.get('project_type', 'unknown').title()}
        - Framework: {env_context.get('framework', 'unknown').title()}
        - Project Root: {env_context.get('project_root', 'N/A')}
        
        INTELLIGENT NATURAL LANGUAGE RESOLUTION:
        
        1. **Context-Driven Command Selection**:
           Use environmental context to choose the most appropriate commands:
           
           - **"find all log files"** → 
             * Python Project: `find . -name "*.log" -o -name "*.out" -o -name "*.err"`
             * Generic: `find . -type f -name "*.log"`
             
           - **"show running processes"** →
             * Linux: `ps aux` or `ps -ef` 
             * Include memory usage: `ps aux --sort=-%mem | head -20`
             
           - **"list files with details"** →
             * Modern: `ls -lah` (human-readable sizes)
             * Sort by time: `ls -lat` 
             
           - **"check git status"** →
             * If in git repo: `git status --short` or `git status`
             * If not in repo: Suggest `git init` or navigate to git directory
           
           - **"show network connections"** →
             * Modern Linux: `ss -tuln` 
             * Traditional: `netstat -tuln`
           
        2. **Pattern Recognition & Smart Defaults**:
           - "all X files" → Use appropriate file extension patterns
           - "running X" → Focus on process/service commands  
           - "show X" → Prefer detailed/verbose output options
           - "find X" → Use context-appropriate search paths and patterns
           - "current X" → Focus on status/info commands
        
        3. **Project-Aware Suggestions**:
           - **Python Projects**: Prioritize `python`, `pip`, `pytest`, `.py` files
           - **Git Repositories**: Include git-context in explanations
           - **Web Projects**: Consider `curl`, `wget`, port-related commands
           - **Development**: Prefer development-friendly command variants
        
        4. **Enhanced Reasoning with Context**:
           Always explain your command choice using available context:
           - "Since this is a Python project, I'm searching for .py files"
           - "Given you're in a git repository, I'm including git status info"
           - "For {platform}, I'm using the {shell}-compatible syntax"
           - "Considering your project structure, I'm searching from project root"
        
        5. **Safety & Alternatives**:
           - Always prioritize safe command variants
           - Suggest alternatives when multiple good options exist
           - Warn about potentially destructive operations
           - Reference context when explaining safety considerations
        
        RESPONSE FORMAT:
        Always respond with valid JSON containing:
        - command: The actual OS command optimized for the current environment
        - explanation: Context-aware explanation referencing environment details
        - confidence: 0.0-1.0 confidence level 
        - safe: Boolean indicating command safety
        - reasoning: Detailed explanation of why this command was chosen using available context
        - context_used: Array of context factors that influenced the decision
        - alternatives: Suggest other valid approaches if applicable
        
        CRITICAL: Use the rich environmental context provided to give more intelligent, relevant, and accurate command translations that feel natural and context-aware to the user.
        """
    
    def _refresh_context_if_needed(self):
        """Refresh persistent context if environment has changed"""
        try:
            current_context = self.shell_adapter.get_enhanced_context()
            
            # Create hash of current context
            import hashlib
            hashable_current = self._make_hashable(current_context)
            context_str = json.dumps(hashable_current, sort_keys=True)
            current_hash = hashlib.md5(context_str.encode()).hexdigest()
            
            # If context changed, refresh it
            if current_hash != self.last_context_hash:
                logger.debug("Context changed, refreshing persistent context")
                self.persistent_context = current_context
                self.last_context_hash = current_hash
                self._create_persistent_system_prompt()
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Failed to refresh context: {e}")
            return False
    
    def _prompt_for_api_key(self) -> bool:
        """Prompt user for OpenAI API key and save it"""
        
        if self._api_key_prompted:
            return False
            
        self._api_key_prompted = True
        
        console.print("\n[yellow]🤖 AI Translation Required[/yellow]")
        console.print("This command requires OpenAI API translation.")
        console.print("You need an OpenAI API key to use AI-powered command translation.")
        console.print("\n[bold]How to get an OpenAI API key:[/bold]")
        console.print("1. Visit: https://platform.openai.com/api-keys")
        console.print("2. Sign up or log in to your OpenAI account")
        console.print("3. Create a new API key")
        console.print("4. Copy the API key")
        
        api_key = Prompt.ask("\n[cyan]Enter your OpenAI API key[/cyan]", password=True)
        
        if not api_key or api_key.strip() == "":
            console.print("[red]No API key provided. AI translation will be unavailable.[/red]")
            return False
        
        # Test the API key
        try:
            test_client = OpenAI(api_key=api_key.strip())
            # Make a simple test call
            test_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            
            # If successful, save the API key
            self.api_key = api_key.strip()
            self.client = test_client
            
            # Save to environment for this session
            os.environ["OPENAI_API_KEY"] = self.api_key
            
            console.print("[green]✓ API key validated and saved for this session![/green]")
            console.print("[dim]Note: To persist the API key, add it to your shell profile:[/dim]")
            console.print(f"[dim]export OPENAI_API_KEY='your_key_here'[/dim]")
            
            return True
            
        except Exception as e:
            console.print(f"[red]Invalid API key: {str(e)}[/red]")
            console.print("[red]AI translation will be unavailable.[/red]")
            return False
    
    def _translate_with_ai(self, natural_language: str, timeout: float, context: Optional[Dict] = None) -> Optional[Dict]:
        """Perform AI translation with timeout using persistent context"""
        
        # Check if we have a valid client, if not try to prompt for API key
        if not self.client:
            if not self._prompt_for_api_key():
                return None
        
        # Refresh context if needed (lightweight check)
        self._refresh_context_if_needed()
        
        def api_call():
            # Use persistent system prompt with rich context
            system_prompt = self.persistent_system_prompt or self._create_system_prompt(context)
            
            # Create enhanced user prompt with natural language analysis
            user_prompt = f"""
            Translate this natural language request to an OS command:
            "{natural_language}"
            
            INTELLIGENT PATTERN RECOGNITION:
            1. **Intent Recognition**: Identify the core intent (find, show, list, check, etc.)
            2. **Object Identification**: What is the user looking for? (files, processes, status, etc.)
            3. **Parameter Extraction**: Recognize file types, modifiers, scopes automatically
            4. **Pattern Understanding**: Automatically understand common patterns like:
               - "find [all] [type] files" → find . -name "*.EXT"
               - "show [thing]" → appropriate display command
               - "list [scope] [objects]" → appropriate listing command
               - "check/show [system component]" → appropriate status command
            
            AUTOMATIC FILE TYPE RECOGNITION:
            - html/HTML files → *.html
            - css/CSS files → *.css  
            - javascript/JS files → *.js
            - python/py files → *.py
            - log files → *.log (or *.log -o *.out -o *.err for comprehensive)
            - text files → *.txt
            - config files → *.conf -o *.config -o *.cfg
            - Any file type mentioned → *.EXT (where EXT is the file extension)
            
            SMART PATTERN VARIATIONS:
            - Recognize "all", "every", "any" as comprehensive search modifiers
            - Understand size qualifiers: "large" → +100M, "small" → -1M
            - Understand time qualifiers: "recent" → -7 days, "old" → +30 days
            
            CONTEXT-DRIVEN TRANSLATION:
            - Leverage the rich system context provided in your system instructions
            - Consider project type, git status, platform, and available commands
            - Choose command variants that make sense for this specific environment
            - Reference context factors in your reasoning
            
            RESPONSE REQUIREMENTS:
            Provide JSON with this exact format:
            {{
                "command": "context-optimized OS command",
                "explanation": "detailed explanation referencing environmental context",
                "confidence": 0.95,
                "safe": true,
                "reasoning": "detailed reasoning using available environmental context",
                "context_used": ["specific context factors that influenced this decision"],
                "alternatives": "other valid approaches if applicable"
            }}
            
            Remember: You have persistent awareness of this environment. Use it to provide smarter, more relevant command translations.
            """
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            if not self.client:
                return None
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using mini for faster response
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,  # Lower temperature for faster, more deterministic responses
                max_tokens=600   # Increased tokens for detailed context-aware explanations
            )
            
            content = response.choices[0].message.content
            if content is None:
                return None
            return json.loads(content)
        
        try:
            # Execute API call with timeout
            future = self.executor.submit(api_call)
            result = future.result(timeout=timeout)
            
            # Check if result is None
            if result is None:
                logger.error("AI response was None")
                return None
            
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
    
    def _create_system_prompt(self, context: Optional[Dict] = None) -> str:
        """Create system prompt based on context"""
        
        if context:
            platform_name = context.get('platform', 'unknown')
            shell_info = context.get('shell', 'unknown')
            os_name = context.get('os_name', 'Unknown')
            architecture = context.get('architecture', 'unknown')
        else:
            # Fallback for backwards compatibility
            platform_name = platform.system().lower()
            shell_info = self._get_shell_info()
            os_name = platform.system()
            architecture = platform.machine()
        
        return f"""
        You are an expert system administrator assistant that translates natural language requests into OS commands.
        
        SYSTEM INFORMATION:
        - Platform: {platform_name}
        - Operating System: {os_name}
        - Shell: {shell_info}
        - Architecture: {architecture}
        
        TRANSLATION RULES:
        1. Always provide commands appropriate for {platform_name} ({os_name})
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
    
    def _get_shell_info(self, context: Optional[Dict] = None) -> str:
        """Get information about the current shell"""
        
        if context:
            return context.get('shell', 'unknown')
        
        # Fallback for backwards compatibility
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
            if not self.client:
                return []
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            if content is None:
                return []
            result = json.loads(content)
            return result.get('suggestions', [])
            
        except Exception as e:
            logger.error(f"Error getting suggestions: {str(e)}")
            return []
    
    def _check_git_context_commands(self, natural_language: str) -> Optional[Dict]:
        """
        Check for Git context-aware commands using GitContextManager
        
        Args:
            natural_language: User's natural language input
            
        Returns:
            Dictionary with command suggestion or None
        """
        try:
            # Get Git context from shell_adapter (Level 1)
            git_context = self.shell_adapter.get_git_context()
            
            # If not in a Git repository, skip Git context suggestions
            if not git_context.get('is_git_repo', False):
                return None
            
            # Use git context manager from shell_adapter
            if not self.shell_adapter.git_context:
                return None
                
            git_state = self.shell_adapter.git_context.get_repository_state()
            git_suggestion = self.shell_adapter.git_context.suggest_git_command(natural_language, git_state)
            
            if git_suggestion:
                # Add safety warnings if any
                warnings = self.shell_adapter.git_context.get_git_safety_warnings(
                    git_suggestion['command'], git_state
                )
                
                # Enhance explanation with context
                explanation = git_suggestion['explanation']
                if warnings:
                    explanation += f"\n\nWarnings: {'; '.join(warnings)}"
                
                # Add Git context information
                context_info = []
                if git_state.current_branch:
                    context_info.append(f"Branch: {git_state.current_branch}")
                if git_state.has_staged_changes:
                    context_info.append(f"Staged files: {len(git_state.staged_files)}")
                if git_state.has_unstaged_changes:
                    context_info.append(f"Unstaged files: {len(git_state.unstaged_files)}")
                if git_state.ahead_commits > 0:
                    context_info.append(f"Ahead by {git_state.ahead_commits} commits")
                if git_state.behind_commits > 0:
                    context_info.append(f"Behind by {git_state.behind_commits} commits")
                
                if context_info:
                    explanation += f"\n\nGit Context: {'; '.join(context_info)}"
                
                return {
                    'command': git_suggestion['command'],
                    'explanation': explanation,
                    'confidence': git_suggestion.get('confidence', 0.9),
                    'cached': False,
                    'instant': True,
                    'git_context_aware': True,
                    'git_state': {
                        'branch': git_state.current_branch,
                        'has_changes': git_state.has_staged_changes or git_state.has_unstaged_changes,
                        'warnings': warnings
                    }
                }
            
            return None
            
        except Exception as e:
            logger.debug(f"Git context check failed: {e}")
            return None
    
    def _check_environment_context_commands(self, natural_language: str) -> Optional[Dict]:
        """
        Check for environment-aware commands using EnvironmentContextManager
        
        Args:
            natural_language: User's natural language input
            
        Returns:
            Dictionary with command suggestion or None
        """
        try:
            # Get environment context from shell_adapter (Level 1)
            env_context = self.shell_adapter.get_environment_context()
            
            # Skip if unknown project type
            if env_context.get('project_type') == 'unknown':
                return None
            
            # Use environment context manager from shell_adapter
            if not self.shell_adapter.env_context:
                return None
                
            # For now, skip environment command suggestions since the API requires ProjectEnvironment object
            # This will be enhanced when we have proper object mapping
            return None
            
            if env_suggestion:
                # Enhance explanation with context
                explanation = env_suggestion['explanation']
                
                # Add environment context information
                context_info = []
                if env_context.get('project_type') != "unknown":
                    context_info.append(f"Project: {env_context['project_type']}")
                if env_context.get('framework'):
                    context_info.append(f"Framework: {env_context['framework']}")
                if env_context.get('package_manager'):
                    context_info.append(f"Package Manager: {env_context['package_manager']}")
                if env_context.get('environment_type', 'development') != "development":
                    context_info.append(f"Environment: {env_context['environment_type']}")
                
                if context_info:
                    explanation += f"\n\nProject Context: {'; '.join(context_info)}"
                
                return {
                    'command': env_suggestion['command'],
                    'explanation': explanation,
                    'confidence': env_suggestion.get('confidence', 0.85),
                    'cached': False,
                    'instant': True,
                    'env_context_aware': True,
                    'project_context': {
                        'type': env_context.get('project_type'),
                        'framework': env_context.get('framework'),
                        'package_manager': env_context.get('package_manager'),
                        'environment': env_context.get('environment_type', 'development')
                    }
                }
            
            return None
            
        except Exception as e:
            logger.debug(f"Environment context check failed: {e}")
            return None
