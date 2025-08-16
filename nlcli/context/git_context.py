"""
Git Context Manager for repository awareness and intelligent Git command suggestions
"""

import os
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from .utils import setup_logging

logger = setup_logging()

@dataclass
class GitRepositoryState:
    """Data structure for Git repository state"""
    is_git_repo: bool = False
    current_branch: str = ""
    remote_branch: str = ""
    ahead_commits: int = 0
    behind_commits: int = 0
    has_staged_changes: bool = False
    has_unstaged_changes: bool = False
    has_untracked_files: bool = False
    in_merge_conflict: bool = False
    staged_files: List[str] = field(default_factory=list)
    unstaged_files: List[str] = field(default_factory=list)
    untracked_files: List[str] = field(default_factory=list)
    repository_root: str = ""
    
    # __post_init__ removed since we use field(default_factory=list)

class GitContextManager:
    """Manages Git repository context and provides intelligent Git command suggestions"""
    
    def __init__(self):
        self.current_directory = os.getcwd()
        self._cached_state = None
        self._cache_timestamp = 0
        self._cache_ttl = 30  # Cache for 30 seconds
    
    def find_git_repository(self, start_path: Optional[str] = None) -> Optional[str]:
        """
        Find Git repository root by traversing up the directory tree
        
        Args:
            start_path: Starting directory (defaults to current directory)
            
        Returns:
            Path to repository root or None if not in a Git repository
        """
        if start_path is None:
            start_path = self.current_directory
        
        current_path = Path(start_path).resolve()
        
        while current_path != current_path.parent:
            git_dir = current_path / '.git'
            if git_dir.exists():
                return str(current_path)
            current_path = current_path.parent
        
        return None
    
    def _run_git_command(self, command: List[str], repository_root: Optional[str] = None) -> Tuple[bool, str]:
        """
        Execute git command safely
        
        Args:
            command: Git command as list of strings
            repository_root: Repository root directory
            
        Returns:
            Tuple of (success, output)
        """
        try:
            original_cwd = None
            if repository_root:
                original_cwd = os.getcwd()
                os.chdir(repository_root)
            
            result = subprocess.run(
                ['git'] + command,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if repository_root and original_cwd:
                os.chdir(original_cwd)
            
            success = result.returncode == 0
            output = result.stdout.strip() if success else result.stderr.strip()
            
            return success, output
            
        except subprocess.TimeoutExpired:
            logger.warning("Git command timed out")
            return False, "Command timed out"
        except Exception as e:
            logger.error(f"Git command failed: {e}")
            return False, str(e)
    
    def get_current_branch(self, repository_root: str) -> str:
        """Get current branch name"""
        success, output = self._run_git_command(['branch', '--show-current'], repository_root)
        return output if success else ""
    
    def get_remote_tracking_branch(self, repository_root: str, branch: str) -> str:
        """Get remote tracking branch for current branch"""
        success, output = self._run_git_command(
            ['config', '--get', f'branch.{branch}.merge'], 
            repository_root
        )
        if success and output:
            # Extract branch name from refs/heads/branch_name
            return output.replace('refs/heads/', '')
        return ""
    
    def get_ahead_behind_count(self, repository_root: str, branch: str, remote_branch: str) -> Tuple[int, int]:
        """Get ahead/behind commit count compared to remote"""
        if not remote_branch:
            return 0, 0
        
        success, output = self._run_git_command(
            ['rev-list', '--left-right', '--count', f'origin/{remote_branch}...{branch}'],
            repository_root
        )
        
        if success and output:
            try:
                behind, ahead = map(int, output.split())
                return ahead, behind
            except ValueError:
                pass
        
        return 0, 0
    
    def get_repository_status(self, repository_root: str) -> Dict:
        """Get detailed repository status"""
        success, output = self._run_git_command(['status', '--porcelain'], repository_root)
        
        if not success:
            return {
                'staged_files': [],
                'unstaged_files': [],
                'untracked_files': [],
                'has_staged_changes': False,
                'has_unstaged_changes': False,
                'has_untracked_files': False
            }
        
        staged_files = []
        unstaged_files = []
        untracked_files = []
        
        for line in output.split('\n'):
            if not line.strip():
                continue
            
            status = line[:2]
            filename = line[3:]
            
            # Staged changes
            if status[0] in 'MADRC':
                staged_files.append(filename)
            
            # Unstaged changes
            if status[1] in 'MD':
                unstaged_files.append(filename)
            
            # Untracked files
            if status == '??':
                untracked_files.append(filename)
        
        return {
            'staged_files': staged_files,
            'unstaged_files': unstaged_files,
            'untracked_files': untracked_files,
            'has_staged_changes': len(staged_files) > 0,
            'has_unstaged_changes': len(unstaged_files) > 0,
            'has_untracked_files': len(untracked_files) > 0
        }
    
    def check_merge_conflict(self, repository_root: str) -> bool:
        """Check if repository is in merge conflict state"""
        merge_head_file = Path(repository_root) / '.git' / 'MERGE_HEAD'
        return merge_head_file.exists()
    
    def get_repository_state(self, force_refresh: bool = False) -> GitRepositoryState:
        """
        Get comprehensive repository state with caching
        
        Args:
            force_refresh: Force refresh of cached state
            
        Returns:
            GitRepositoryState object with current repository information
        """
        import time
        
        current_time = time.time()
        
        # Return cached state if still valid
        if (not force_refresh and 
            self._cached_state and 
            current_time - self._cache_timestamp < self._cache_ttl):
            return self._cached_state
        
        # Find repository
        repository_root = self.find_git_repository()
        
        if not repository_root:
            state = GitRepositoryState(is_git_repo=False)
            self._cached_state = state
            self._cache_timestamp = current_time
            return state
        
        # Get current branch
        current_branch = self.get_current_branch(repository_root)
        
        # Get remote tracking branch
        remote_branch = self.get_remote_tracking_branch(repository_root, current_branch)
        
        # Get ahead/behind count
        ahead_commits, behind_commits = self.get_ahead_behind_count(
            repository_root, current_branch, remote_branch
        )
        
        # Get repository status
        status_info = self.get_repository_status(repository_root)
        
        # Check merge conflict
        in_merge_conflict = self.check_merge_conflict(repository_root)
        
        # Create state object
        state = GitRepositoryState(
            is_git_repo=True,
            current_branch=current_branch,
            remote_branch=remote_branch,
            ahead_commits=ahead_commits,
            behind_commits=behind_commits,
            has_staged_changes=status_info['has_staged_changes'],
            has_unstaged_changes=status_info['has_unstaged_changes'],
            has_untracked_files=status_info['has_untracked_files'],
            in_merge_conflict=in_merge_conflict,
            staged_files=status_info['staged_files'],
            unstaged_files=status_info['unstaged_files'],
            untracked_files=status_info['untracked_files'],
            repository_root=repository_root
        )
        
        # Cache the state
        self._cached_state = state
        self._cache_timestamp = current_time
        
        logger.debug(f"Git state updated: {current_branch}, {len(status_info['staged_files'])} staged files")
        
        return state
    
    def suggest_git_command(self, natural_language: str, context_state: Optional[GitRepositoryState] = None) -> Optional[Dict]:
        """
        Suggest Git command based on natural language and repository context
        
        Args:
            natural_language: User's natural language input
            context_state: Current repository state
            
        Returns:
            Dictionary with suggested command and explanation
        """
        if context_state is None:
            context_state = self.get_repository_state()
        
        if not context_state.is_git_repo:
            return None
        
        text_lower = natural_language.lower()
        
        # Common Git patterns with context awareness
        git_patterns = [
            # Status and information
            {
                'patterns': ['status', 'what changed', 'show changes', 'git state'],
                'command': 'git status',
                'explanation': 'Show repository status and changes',
                'confidence': 0.95
            },
            
            # Commit operations
            {
                'patterns': ['commit', 'save changes', 'commit my work'],
                'command': self._get_smart_commit_command(context_state),
                'explanation': 'Commit staged changes with appropriate message',
                'confidence': 0.9
            },
            
            # Branch operations
            {
                'patterns': ['switch to main', 'go to main', 'checkout main'],
                'command': self._get_safe_branch_switch_command('main', context_state),
                'explanation': 'Safely switch to main branch',
                'confidence': 0.95
            },
            
            # Push/pull operations
            {
                'patterns': ['push', 'push changes', 'upload changes'],
                'command': self._get_smart_push_command(context_state),
                'explanation': 'Push changes to remote repository',
                'confidence': 0.9
            },
            
            {
                'patterns': ['pull', 'get latest', 'fetch changes', 'update'],
                'command': f'git pull origin {context_state.remote_branch}' if context_state.remote_branch else 'git pull',
                'explanation': 'Pull latest changes from remote',
                'confidence': 0.9
            }
        ]
        
        # Find matching pattern
        for pattern_info in git_patterns:
            for pattern in pattern_info['patterns']:
                if pattern in text_lower:
                    return {
                        'command': pattern_info['command'],
                        'explanation': pattern_info['explanation'],
                        'confidence': pattern_info['confidence'],
                        'context_aware': True,
                        'git_context': True
                    }
        
        return None
    
    def _get_smart_commit_command(self, state: GitRepositoryState) -> str:
        """Generate smart commit command based on repository state"""
        if not state.has_staged_changes and state.has_unstaged_changes:
            return 'git add . && git commit -m "Update: staged and commit changes"'
        elif state.has_staged_changes:
            return 'git commit -m "Update: commit staged changes"'
        else:
            return 'git add . && git commit -m "Update: stage and commit all changes"'
    
    def _get_safe_branch_switch_command(self, target_branch: str, state: GitRepositoryState) -> str:
        """Generate safe branch switch command with appropriate warnings"""
        if state.has_unstaged_changes or state.has_staged_changes:
            return f'git stash && git checkout {target_branch}'
        else:
            return f'git checkout {target_branch}'
    
    def _get_smart_push_command(self, state: GitRepositoryState) -> str:
        """Generate smart push command based on remote tracking"""
        if state.remote_branch:
            return f'git push origin {state.current_branch}'
        else:
            return f'git push -u origin {state.current_branch}'
    
    def generate_commit_message(self, state: GitRepositoryState) -> str:
        """Generate intelligent commit message based on changes"""
        if not state.staged_files and not state.unstaged_files:
            return "Update: general changes"
        
        files = state.staged_files + state.unstaged_files
        
        # Analyze file types for better commit messages
        has_docs = any(f.endswith(('.md', '.txt', '.rst')) for f in files)
        has_tests = any('test' in f.lower() for f in files)
        has_config = any(f.endswith(('.json', '.yml', '.yaml', '.toml', '.ini')) for f in files)
        has_code = any(f.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c')) for f in files)
        
        if has_tests:
            return "test: update test files"
        elif has_docs:
            return "docs: update documentation"
        elif has_config:
            return "config: update configuration files"
        elif has_code:
            return "feat: update code implementation"
        else:
            return f"update: modify {len(files)} file{'s' if len(files) > 1 else ''}"
    
    def get_git_safety_warnings(self, command: str, state: GitRepositoryState) -> List[str]:
        """Get safety warnings for Git commands"""
        warnings = []
        
        if 'force' in command.lower() or '-f' in command:
            warnings.append("⚠️  Force operation detected - this may overwrite changes")
        
        if 'reset --hard' in command:
            warnings.append("⚠️  Hard reset will permanently delete uncommitted changes")
        
        if 'push' in command and state.has_unstaged_changes:
            warnings.append("💡 You have unstaged changes that won't be pushed")
        
        if 'checkout' in command and (state.has_unstaged_changes or state.has_staged_changes):
            warnings.append("💡 Consider stashing changes before switching branches")
        
        if state.in_merge_conflict and 'merge' in command:
            warnings.append("⚠️  Repository is in merge conflict state")
        
        return warnings