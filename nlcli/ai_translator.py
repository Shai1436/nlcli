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
from .utils import get_platform_info, setup_logging
from .cache_manager import CacheManager

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
        self.platform_info = get_platform_info()
        
        # Performance optimizations
        self.enable_cache = enable_cache
        self.cache_manager = CacheManager() if enable_cache else None
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Context awareness
        from .context_manager import ContextManager
        config_dir = os.path.expanduser('~/.nlcli')
        self.context_manager = ContextManager(config_dir)
        
        # Command filter for direct execution
        from .command_filter import CommandFilter
        self.command_filter = CommandFilter()
        
        # Typo corrector for enhanced recognition
        from .typo_corrector import TypoCorrector
        self.typo_corrector = TypoCorrector()
        
        # Common command patterns for instant recognition (50+ patterns)
        self.instant_patterns = {
            # File and Directory Operations
            'ls': ['list files', 'show files', 'list directory', 'dir', 'what files', 'show contents'],
            'ls -la': ['list all files', 'show hidden files', 'detailed list', 'list with details', 'show file details'],
            'ls -lh': ['list files with sizes', 'show file sizes', 'human readable list', 'list with size'],
            'pwd': ['current directory', 'where am i', 'current path', 'show path', 'current location'],
            'cd': ['change directory', 'go to', 'navigate to', 'move to directory'],
            'cd ..': ['go back', 'parent directory', 'go up', 'previous directory'],
            'cd ~': ['go home', 'home directory', 'user directory'],
            'cat': ['show file', 'read file', 'display file', 'view file', 'print file'],
            'head': ['show first lines', 'beginning of file', 'first 10 lines'],
            'tail': ['show last lines', 'end of file', 'last 10 lines'],
            'tail -f': ['follow file', 'watch file', 'monitor file', 'tail file'],
            'less': ['page through file', 'view file page', 'scroll file'],
            'more': ['view file', 'page file', 'read file pages'],
            'mkdir': ['create directory', 'make folder', 'new folder', 'create folder'],
            'mkdir -p': ['create nested directories', 'make directory tree', 'create path'],
            'rmdir': ['remove directory', 'delete folder', 'remove folder'],
            'rm': ['delete file', 'remove file', 'delete'],
            'rm -rf': ['force delete', 'delete recursively', 'remove all'],
            'cp': ['copy file', 'duplicate file', 'copy'],
            'cp -r': ['copy directory', 'copy folder', 'recursive copy'],
            'mv': ['move file', 'rename file', 'move'],
            'touch': ['create file', 'new file', 'make file'],
            'find .': ['find files', 'search files', 'locate files'],
            'locate': ['find file location', 'search for file'],
            'which': ['find command', 'locate command', 'where is command'],
            'ln -s': ['create link', 'symbolic link', 'symlink'],
            
            # File Content and Text Processing
            'grep': ['search in file', 'find text', 'search text'],
            'sort': ['sort file', 'sort lines', 'arrange lines'],
            'uniq': ['unique lines', 'remove duplicates', 'filter duplicates'],
            'wc': ['count words', 'word count', 'line count'],
            'wc -l': ['count lines', 'number of lines', 'line count'],
            'diff': ['compare files', 'file difference', 'diff files'],
            'cut': ['extract columns', 'cut fields', 'select columns'],
            'awk': ['process text', 'extract fields', 'text processing'],
            'sed': ['replace text', 'substitute text', 'edit text'],
            
            # System Information and Monitoring
            'ps': ['show processes', 'list processes', 'running processes'],
            'ps aux': ['all processes', 'detailed processes', 'process list'],
            'top': ['system monitor', 'cpu usage', 'memory usage', 'resource monitor'],
            'htop': ['interactive top', 'better top', 'system stats'],
            'df': ['disk usage', 'disk space', 'storage usage'],
            'df -h': ['disk space human readable', 'storage info', 'disk info'],
            'du': ['directory size', 'folder size', 'space used'],
            'du -sh': ['folder size summary', 'directory size human'],
            'free': ['memory usage', 'ram usage', 'memory info'],
            'free -h': ['memory info human readable', 'ram info'],
            'uname': ['system info', 'os info', 'kernel info'],
            'uname -a': ['detailed system info', 'full system info'],
            'uptime': ['system uptime', 'how long running', 'boot time'],
            'whoami': ['current user', 'username', 'who am i'],
            'id': ['user id', 'user info', 'group info'],
            'w': ['who is logged in', 'logged users', 'user activity'],
            'last': ['login history', 'last logins', 'user sessions'],
            
            # Network and Connectivity
            'ping': ['test connection', 'check connectivity', 'network test'],
            'wget': ['download file', 'fetch file', 'get file'],
            'curl': ['web request', 'http request', 'fetch url'],
            'netstat': ['network connections', 'open ports', 'network status'],
            'ss': ['socket statistics', 'network sockets', 'connection info'],
            'ifconfig': ['network interface', 'ip address', 'network config'],
            'ip addr': ['show ip', 'network interfaces', 'ip info'],
            
            # Archives and Compression
            'tar -xzf': ['extract tar', 'unpack tar', 'decompress tar'],
            'tar -czf': ['create tar', 'compress tar', 'make archive'],
            'zip': ['create zip', 'compress files', 'make zip'],
            'unzip': ['extract zip', 'decompress zip', 'unpack zip'],
            'gzip': ['compress file', 'gzip file'],
            'gunzip': ['decompress file', 'unzip file'],
            
            # File Permissions and Ownership
            'chmod': ['change permissions', 'file permissions', 'modify permissions'],
            'chmod +x': ['make executable', 'add execute permission'],
            'chown': ['change owner', 'file owner', 'change ownership'],
            'chgrp': ['change group', 'file group'],
            
            # Environment and Variables
            'env': ['environment variables', 'show variables', 'environment'],
            'export': ['set variable', 'environment variable'],
            'echo': ['print text', 'display text', 'show text'],
            'date': ['current time', 'show date', 'what time', 'current date'],
            'cal': ['calendar', 'show calendar', 'current month'],
            'history': ['command history', 'previous commands', 'past commands'],
            'alias': ['command aliases', 'shortcuts', 'command shortcuts'],
            
            # Terminal and Session
            'clear': ['clear screen', 'clean terminal', 'clear terminal'],
            'reset': ['reset terminal', 'fix terminal'],
            'exit': ['quit', 'logout', 'close terminal'],
            'logout': ['log out', 'end session'],
            'screen': ['new session', 'terminal session'],
            'tmux': ['terminal multiplexer', 'multiple terminals'],
            
            # Package Management (Linux)
            'sudo apt update': ['update packages', 'refresh packages', 'update package list'],
            'sudo apt upgrade': ['upgrade system', 'update all packages'],
            'sudo apt install': ['install package', 'add software'],
            'apt search': ['search packages', 'find software'],
            'dpkg -l': ['list installed packages', 'installed software'],
            
            # Git Commands
            'git status': ['git status', 'repo status', 'working tree status'],
            'git log': ['git history', 'commit history', 'git commits'],
            'git diff': ['git changes', 'file changes', 'working changes'],
            'git add .': ['stage all changes', 'add all files'],
            'git commit': ['commit changes', 'save changes'],
            'git push': ['push to remote', 'upload changes'],
            'git pull': ['pull changes', 'update from remote'],
            'git clone': ['clone repository', 'copy repo']
        }
        
    def translate(self, natural_language: str, timeout: float = 8.0) -> Optional[Dict]:
        """
        Translate natural language to OS command with performance optimizations
        
        Args:
            natural_language: User's natural language input
            timeout: Maximum time to wait for API response
            
        Returns:
            Dictionary containing command, explanation, and confidence
        """
        
        try:
            # Step 0: Try typo correction first
            corrected_input = self.typo_corrector.correct_typo(natural_language)
            if corrected_input != natural_language:
                logger.debug(f"Typo corrected: '{natural_language}' -> '{corrected_input}'")
                # Use corrected input for further processing
                natural_language = corrected_input
            
            # Step 1: Check for direct command execution (fastest)
            if self.command_filter.is_direct_command(natural_language):
                direct_result = self.command_filter.get_direct_command_result(natural_language)
                if direct_result:
                    logger.debug(f"Direct command match for: {natural_language}")
                    return {
                        **direct_result,
                        'cached': False,
                        'instant': True,
                        'typo_corrected': corrected_input != natural_language
                    }
            
            # Step 2: Check for instant pattern matches (sub-millisecond response)
            instant_result = self._check_instant_patterns(natural_language)
            if instant_result:
                logger.debug(f"Instant pattern match for: {natural_language}")
                return instant_result
            
            # Step 2.5: Try fuzzy matching for typos and variations
            fuzzy_result = self.typo_corrector.fuzzy_match(natural_language, threshold=0.7)
            if fuzzy_result:
                command, confidence = fuzzy_result
                logger.debug(f"Fuzzy match found: '{natural_language}' -> '{command}' (confidence: {confidence:.2f})")
                return {
                    'command': command,
                    'explanation': self._get_command_explanation(command),
                    'confidence': confidence,
                    'cached': False,
                    'instant': True,
                    'fuzzy_matched': True
                }
            
            # Step 1.5: Check context-aware suggestions
            context_suggestions = self.context_manager.get_context_suggestions(natural_language)
            if context_suggestions:
                # Use the highest confidence context suggestion
                best_suggestion = max(context_suggestions, key=lambda x: x['confidence'])
                if best_suggestion['confidence'] > 0.85:
                    logger.debug(f"Context suggestion for: {natural_language}")
                    return {
                        'command': best_suggestion['command'],
                        'explanation': best_suggestion['explanation'],
                        'confidence': best_suggestion['confidence'],
                        'instant': True,
                        'cached': False,
                        'context_aware': True,
                        'context_type': best_suggestion['context_type']
                    }
            
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
    
    def _translate_with_ai(self, natural_language: str, timeout: float) -> Optional[Dict]:
        """Perform AI translation with timeout"""
        
        # Check if we have a valid client, if not try to prompt for API key
        if not self.client:
            if not self._prompt_for_api_key():
                return None
        
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
