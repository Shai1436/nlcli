"""
Interactive Command Selection module for handling ambiguous natural language requests
"""

import os
from typing import Dict, List, Optional, Tuple
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from rich.panel import Panel
from .utils import setup_logging

logger = setup_logging()
console = Console()

class CommandSelector:
    """Handles interactive command selection when multiple options are available"""
    
    def __init__(self):
        """Initialize command selector with predefined ambiguous patterns"""
        
        # Define common ambiguous requests and their possible interpretations
        self.ambiguous_patterns = {
            # File operations
            'copy file': [
                {'command': 'cp {source} {dest}', 'description': 'Copy file locally', 'use_case': 'Local file copying'},
                {'command': 'rsync -av {source} {dest}', 'description': 'Copy with progress and verification', 'use_case': 'Large files or with progress'},
                {'command': 'scp {source} user@host:{dest}', 'description': 'Copy file over SSH', 'use_case': 'Remote file transfer'}
            ],
            
            'move file': [
                {'command': 'mv {source} {dest}', 'description': 'Move/rename file', 'use_case': 'Standard move operation'},
                {'command': 'rsync --remove-source-files {source} {dest}', 'description': 'Move with verification', 'use_case': 'Large files with safety'}
            ],
            
            'delete file': [
                {'command': 'rm {file}', 'description': 'Delete file', 'use_case': 'Single file deletion'},
                {'command': 'rm -i {file}', 'description': 'Delete with confirmation', 'use_case': 'Safety confirmation'},
                {'command': 'rm -rf {file}', 'description': 'Force delete recursively', 'use_case': 'Directories and stubborn files'},
                {'command': 'trash {file}', 'description': 'Move to trash (if available)', 'use_case': 'Recoverable deletion'}
            ],
            
            # Text processing
            'search text': [
                {'command': 'grep "{pattern}" {file}', 'description': 'Search in specific file', 'use_case': 'Single file search'},
                {'command': 'grep -r "{pattern}" .', 'description': 'Search recursively in directory', 'use_case': 'Directory-wide search'},
                {'command': 'ag "{pattern}"', 'description': 'Fast search with Silver Searcher', 'use_case': 'Large codebases'},
                {'command': 'find . -name "*{pattern}*"', 'description': 'Search by filename', 'use_case': 'Find files by name'}
            ],
            
            'replace text': [
                {'command': 'sed -i "s/{old}/{new}/g" {file}', 'description': 'Replace in file directly', 'use_case': 'Quick replacements'},
                {'command': 'sed "s/{old}/{new}/g" {file} > {newfile}', 'description': 'Replace and save to new file', 'use_case': 'Safe replacements'},
                {'command': 'find . -type f -exec sed -i "s/{old}/{new}/g" {} +', 'description': 'Replace across multiple files', 'use_case': 'Bulk replacements'}
            ],
            
            # Process management
            'kill process': [
                {'command': 'kill {pid}', 'description': 'Terminate process gracefully', 'use_case': 'Standard termination'},
                {'command': 'kill -9 {pid}', 'description': 'Force kill process', 'use_case': 'Unresponsive processes'},
                {'command': 'killall {name}', 'description': 'Kill all processes by name', 'use_case': 'Multiple instances'},
                {'command': 'pkill -f {pattern}', 'description': 'Kill by command pattern', 'use_case': 'Complex process matching'}
            ],
            
            'show processes': [
                {'command': 'ps aux', 'description': 'Show all processes (detailed)', 'use_case': 'Complete process list'},
                {'command': 'ps aux | grep {name}', 'description': 'Find specific process', 'use_case': 'Search for specific process'},
                {'command': 'top', 'description': 'Interactive process monitor', 'use_case': 'Real-time monitoring'},
                {'command': 'htop', 'description': 'Enhanced interactive monitor', 'use_case': 'Better visualization'}
            ],
            
            # Network operations
            'download file': [
                {'command': 'wget {url}', 'description': 'Download with wget', 'use_case': 'Standard downloading'},
                {'command': 'curl -O {url}', 'description': 'Download with curl', 'use_case': 'More control over request'},
                {'command': 'curl -L -o {filename} {url}', 'description': 'Download with custom name', 'use_case': 'Specific filename needed'}
            ],
            
            'test connection': [
                {'command': 'ping {host}', 'description': 'Basic connectivity test', 'use_case': 'Simple reachability'},
                {'command': 'telnet {host} {port}', 'description': 'Test specific port', 'use_case': 'Port connectivity'},
                {'command': 'nc -zv {host} {port}', 'description': 'Port scan with netcat', 'use_case': 'Quick port check'},
                {'command': 'curl -I {url}', 'description': 'HTTP connectivity test', 'use_case': 'Web service check'}
            ],
            
            # Archive operations
            'extract archive': [
                {'command': 'tar -xzf {file}', 'description': 'Extract tar.gz archive', 'use_case': '.tar.gz files'},
                {'command': 'tar -xjf {file}', 'description': 'Extract tar.bz2 archive', 'use_case': '.tar.bz2 files'},
                {'command': 'unzip {file}', 'description': 'Extract zip archive', 'use_case': '.zip files'},
                {'command': 'tar -tf {file}', 'description': 'List archive contents', 'use_case': 'Preview before extracting'}
            ],
            
            'create archive': [
                {'command': 'tar -czf {archive}.tar.gz {files}', 'description': 'Create gzip compressed archive', 'use_case': 'Standard compression'},
                {'command': 'tar -cjf {archive}.tar.bz2 {files}', 'description': 'Create bzip2 compressed archive', 'use_case': 'Better compression'},
                {'command': 'zip -r {archive}.zip {files}', 'description': 'Create zip archive', 'use_case': 'Windows compatibility'}
            ],
            
            # System monitoring
            'check disk space': [
                {'command': 'df -h', 'description': 'Show disk usage by filesystem', 'use_case': 'Overall disk usage'},
                {'command': 'du -sh *', 'description': 'Show directory sizes', 'use_case': 'Current directory breakdown'},
                {'command': 'du -sh {path}', 'description': 'Show specific directory size', 'use_case': 'Specific path analysis'},
                {'command': 'ncdu', 'description': 'Interactive disk usage analyzer', 'use_case': 'Detailed exploration'}
            ],
            
            'check memory': [
                {'command': 'free -h', 'description': 'Show memory usage', 'use_case': 'Current memory status'},
                {'command': 'free -h -s 2', 'description': 'Monitor memory continuously', 'use_case': 'Real-time monitoring'},
                {'command': 'cat /proc/meminfo', 'description': 'Detailed memory information', 'use_case': 'Comprehensive memory data'}
            ]
        }
        
        # Track user preferences for learning
        self.user_preferences = {}
        self.usage_stats = {}
    
    def is_ambiguous(self, natural_language: str) -> bool:
        """Check if a natural language request has multiple possible interpretations"""
        
        normalized = natural_language.lower().strip()
        
        # Check direct matches first
        if normalized in self.ambiguous_patterns:
            return True
        
        # Check for exact pattern matches (stricter matching)
        for pattern in self.ambiguous_patterns:
            # Only consider ambiguous if it's a close match to the pattern
            pattern_words = set(pattern.split())
            input_words = set(normalized.split())
            
            # Check if at least 2 key words match and input is similar length
            common_words = pattern_words.intersection(input_words)
            if len(common_words) >= 2 and len(input_words) <= len(pattern_words) + 2:
                return True
        
        return False
    
    def get_command_options(self, natural_language: str) -> List[Dict]:
        """Get possible command options for an ambiguous request"""
        
        normalized = natural_language.lower().strip()
        
        # Direct match
        if normalized in self.ambiguous_patterns:
            return self.ambiguous_patterns[normalized]
        
        # Find best partial match
        best_match = None
        best_score = 0
        
        for pattern, options in self.ambiguous_patterns.items():
            # Calculate match score based on common words
            pattern_words = set(pattern.split())
            input_words = set(normalized.split())
            common_words = pattern_words.intersection(input_words)
            
            if common_words:
                score = len(common_words) / len(pattern_words)
                if score > best_score:
                    best_score = score
                    best_match = options
        
        return best_match or []
    
    def present_options(self, natural_language: str, options: List[Dict]) -> Optional[Dict]:
        """Present command options to user and get their selection"""
        
        if not options:
            return None
        
        # If only one option, return it directly
        if len(options) == 1:
            return options[0]
        
        console.print(f"\n[yellow]Multiple commands available for:[/yellow] [bold]{natural_language}[/bold]")
        
        # Create options table
        table = Table(title="Command Options", show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=3)
        table.add_column("Command", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Best For", style="green")
        
        for i, option in enumerate(options, 1):
            table.add_row(
                str(i),
                option['command'],
                option['description'],
                option['use_case']
            )
        
        console.print(table)
        
        # Get user selection
        try:
            choice = IntPrompt.ask(
                "\n[cyan]Select option (number)[/cyan]",
                choices=[str(i) for i in range(1, len(options) + 1)],
                default="1"
            )
            
            selected_option = options[choice - 1]
            
            # Track user preference for learning
            self._record_user_choice(natural_language, selected_option)
            
            return selected_option
            
        except (KeyboardInterrupt, EOFError):
            console.print("\n[red]Selection cancelled[/red]")
            return None
    
    def _record_user_choice(self, natural_language: str, selected_option: Dict):
        """Record user choice for future learning"""
        
        pattern = natural_language.lower().strip()
        command = selected_option['command']
        
        if pattern not in self.user_preferences:
            self.user_preferences[pattern] = {}
        
        if command not in self.user_preferences[pattern]:
            self.user_preferences[pattern][command] = 0
        
        self.user_preferences[pattern][command] += 1
        
        # Track overall usage stats
        if command not in self.usage_stats:
            self.usage_stats[command] = 0
        self.usage_stats[command] += 1
        
        logger.debug(f"Recorded preference: {pattern} -> {command}")
    
    def get_preferred_option(self, natural_language: str, options: List[Dict]) -> Optional[Dict]:
        """Get user's preferred option based on history, or None if no clear preference"""
        
        pattern = natural_language.lower().strip()
        
        if pattern not in self.user_preferences:
            return None
        
        # Find the most commonly chosen option
        preferences = self.user_preferences[pattern]
        if not preferences:
            return None
        
        most_used_command = max(preferences.keys(), key=lambda k: preferences[k])
        
        # Return the option that matches the most used command
        for option in options:
            if option['command'] == most_used_command:
                # Only auto-select if used more than once
                if preferences[most_used_command] > 1:
                    return option
                break
        
        return None
    
    def suggest_parameters(self, command_template: str, natural_language: str) -> str:
        """Suggest parameter values based on natural language context"""
        
        # Extract potential parameters from natural language
        words = natural_language.split()
        
        # Common parameter patterns
        replacements = {
            '{source}': self._extract_source_path(words),
            '{dest}': self._extract_dest_path(words),
            '{file}': self._extract_file_name(words),
            '{pattern}': self._extract_search_pattern(words),
            '{old}': self._extract_old_text(words),
            '{new}': self._extract_new_text(words),
            '{pid}': self._extract_process_id(words),
            '{name}': self._extract_process_name(words),
            '{url}': self._extract_url(words),
            '{host}': self._extract_hostname(words),
            '{port}': self._extract_port(words),
            '{path}': self._extract_path(words)
        }
        
        # Apply replacements
        result = command_template
        for placeholder, value in replacements.items():
            if placeholder in result and value:
                result = result.replace(placeholder, value)
        
        return result
    
    def _extract_source_path(self, words: List[str]) -> str:
        """Extract source path from words"""
        # Look for common indicators
        for i, word in enumerate(words):
            if word in ['from', 'source']:
                if i + 1 < len(words):
                    return words[i + 1]
        
        # Look for file extensions or paths
        for word in words:
            if '.' in word or '/' in word:
                return word
        
        return ''
    
    def _extract_dest_path(self, words: List[str]) -> str:
        """Extract destination path from words"""
        for i, word in enumerate(words):
            if word in ['to', 'destination', 'dest']:
                if i + 1 < len(words):
                    return words[i + 1]
        return ''
    
    def _extract_file_name(self, words: List[str]) -> str:
        """Extract file name from words"""
        for word in words:
            if '.' in word and not word.startswith('.'):
                return word
        return ''
    
    def _extract_search_pattern(self, words: List[str]) -> str:
        """Extract search pattern from words"""
        # Look for quoted strings or specific patterns
        text = ' '.join(words)
        if '"' in text:
            start = text.find('"')
            end = text.find('"', start + 1)
            if end > start:
                return text[start + 1:end]
        
        # Look for 'for' keyword
        try:
            idx = words.index('for')
            if idx + 1 < len(words):
                return words[idx + 1]
        except ValueError:
            pass
        
        return ''
    
    def _extract_old_text(self, words: List[str]) -> str:
        """Extract old text for replacement"""
        try:
            idx = words.index('replace')
            if idx + 1 < len(words):
                return words[idx + 1]
        except ValueError:
            pass
        return ''
    
    def _extract_new_text(self, words: List[str]) -> str:
        """Extract new text for replacement"""
        try:
            idx = words.index('with')
            if idx + 1 < len(words):
                return words[idx + 1]
        except ValueError:
            pass
        return ''
    
    def _extract_process_id(self, words: List[str]) -> str:
        """Extract process ID from words"""
        for word in words:
            if word.isdigit():
                return word
        return ''
    
    def _extract_process_name(self, words: List[str]) -> str:
        """Extract process name from words"""
        # Common process-related words to skip
        skip_words = {'kill', 'process', 'show', 'find', 'stop', 'terminate'}
        for word in words:
            if word not in skip_words and not word.isdigit():
                return word
        return ''
    
    def _extract_url(self, words: List[str]) -> str:
        """Extract URL from words"""
        for word in words:
            if word.startswith(('http://', 'https://', 'ftp://')):
                return word
        return ''
    
    def _extract_hostname(self, words: List[str]) -> str:
        """Extract hostname from words"""
        for word in words:
            if '.' in word and not word.startswith('.'):
                return word
        return ''
    
    def _extract_port(self, words: List[str]) -> str:
        """Extract port number from words"""
        for word in words:
            if word.isdigit() and 1 <= int(word) <= 65535:
                return word
        return ''
    
    def _extract_path(self, words: List[str]) -> str:
        """Extract file path from words"""
        for word in words:
            if '/' in word or word.startswith('~'):
                return word
        return ''