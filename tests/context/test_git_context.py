#!/usr/bin/env python3
"""
Comprehensive tests for git_context.py - improving coverage from 0% to 95%+
"""

import pytest
import os
import time
import tempfile
import subprocess
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path

from nlcli.context.git_context import GitContextManager, GitRepositoryState


class TestGitRepositoryState:
    """Test GitRepositoryState dataclass"""
    
    def test_git_repository_state_creation_defaults(self):
        """Test GitRepositoryState creation with default values"""
        state = GitRepositoryState()
        
        assert state.is_git_repo is False
        assert state.current_branch == ""
        assert state.remote_branch == ""
        assert state.ahead_commits == 0
        assert state.behind_commits == 0
        assert state.has_staged_changes is False
        assert state.has_unstaged_changes is False
        assert state.has_untracked_files is False
        assert state.in_merge_conflict is False
        assert state.staged_files == []
        assert state.unstaged_files == []
        assert state.untracked_files == []
        assert state.repository_root == ""
    
    def test_git_repository_state_creation_with_values(self):
        """Test GitRepositoryState creation with custom values"""
        state = GitRepositoryState(
            is_git_repo=True,
            current_branch="feature/test",
            remote_branch="main",
            ahead_commits=2,
            behind_commits=1,
            has_staged_changes=True,
            has_unstaged_changes=True,
            has_untracked_files=True,
            in_merge_conflict=True,
            staged_files=['file1.py'],
            unstaged_files=['file2.py'],
            untracked_files=['file3.py'],
            repository_root='/repo'
        )
        
        assert state.is_git_repo is True
        assert state.current_branch == "feature/test"
        assert state.remote_branch == "main"
        assert state.ahead_commits == 2
        assert state.behind_commits == 1
        assert state.has_staged_changes is True
        assert state.has_unstaged_changes is True
        assert state.has_untracked_files is True
        assert state.in_merge_conflict is True
        assert state.staged_files == ['file1.py']
        assert state.unstaged_files == ['file2.py']
        assert state.untracked_files == ['file3.py']
        assert state.repository_root == '/repo'
    
    def test_git_repository_state_field_factories(self):
        """Test that field factories create separate instances"""
        state1 = GitRepositoryState()
        state2 = GitRepositoryState()
        
        # Modify one instance
        state1.staged_files.append('test1.py')
        state1.unstaged_files.append('test2.py')
        state1.untracked_files.append('test3.py')
        
        # Other instance should be unaffected
        assert state2.staged_files == []
        assert state2.unstaged_files == []
        assert state2.untracked_files == []


class TestGitContextManagerInitialization:
    """Test GitContextManager initialization"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test manager initialization"""
        with patch('os.getcwd', return_value='/test/dir'):
            manager = GitContextManager()
        
        assert manager.current_directory == '/test/dir'
        assert manager._cached_state is None
        assert manager._cache_timestamp == 0
        assert manager._cache_ttl == 30


class TestGitRepositoryFinding:
    """Test Git repository finding functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = GitContextManager()
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_find_git_repository_in_root(self):
        """Test finding Git repository in current directory"""
        # Create .git directory
        git_dir = Path(self.temp_dir) / '.git'
        git_dir.mkdir()
        
        repo_root = self.manager.find_git_repository(self.temp_dir)
        assert repo_root == self.temp_dir
    
    def test_find_git_repository_in_parent(self):
        """Test finding Git repository in parent directory"""
        # Create .git in parent directory
        git_dir = Path(self.temp_dir) / '.git'
        git_dir.mkdir()
        
        # Create subdirectory
        sub_dir = Path(self.temp_dir) / 'subdir'
        sub_dir.mkdir()
        
        repo_root = self.manager.find_git_repository(str(sub_dir))
        assert repo_root == self.temp_dir
    
    def test_find_git_repository_nested_structure(self):
        """Test finding Git repository in deeply nested structure"""
        # Create .git in root
        git_dir = Path(self.temp_dir) / '.git'
        git_dir.mkdir()
        
        # Create nested subdirectories
        nested_dir = Path(self.temp_dir) / 'level1' / 'level2' / 'level3'
        nested_dir.mkdir(parents=True)
        
        repo_root = self.manager.find_git_repository(str(nested_dir))
        assert repo_root == self.temp_dir
    
    def test_find_git_repository_not_found(self):
        """Test when Git repository is not found"""
        repo_root = self.manager.find_git_repository(self.temp_dir)
        assert repo_root is None
    
    def test_find_git_repository_default_directory(self):
        """Test finding Git repository using default directory"""
        git_dir = Path(self.temp_dir) / '.git'
        git_dir.mkdir()
        
        with patch('os.getcwd', return_value=self.temp_dir):
            manager = GitContextManager()
            repo_root = manager.find_git_repository()
            assert repo_root == self.temp_dir
    
    def test_find_git_repository_traverses_to_root(self):
        """Test that traversal stops at filesystem root"""
        # Use a path that definitely won't have .git
        non_git_path = '/tmp'
        repo_root = self.manager.find_git_repository(non_git_path)
        assert repo_root is None


class TestGitCommandExecution:
    """Test Git command execution functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = GitContextManager()
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('subprocess.run')
    def test_run_git_command_success(self, mock_run):
        """Test successful Git command execution"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = 'test output'
        mock_result.stderr = ''
        mock_run.return_value = mock_result
        
        success, output = self.manager._run_git_command(['status'])
        
        assert success is True
        assert output == 'test output'
        mock_run.assert_called_once_with(
            ['git', 'status'],
            capture_output=True,
            text=True,
            timeout=10
        )
    
    @patch('subprocess.run')
    def test_run_git_command_failure(self, mock_run):
        """Test failed Git command execution"""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ''
        mock_result.stderr = 'error message'
        mock_run.return_value = mock_result
        
        success, output = self.manager._run_git_command(['invalid-command'])
        
        assert success is False
        assert output == 'error message'
    
    @patch('subprocess.run')
    def test_run_git_command_with_repository_root(self, mock_run):
        """Test Git command execution with repository root"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = 'test output'
        mock_run.return_value = mock_result
        
        with patch('os.getcwd') as mock_getcwd, patch('os.chdir') as mock_chdir:
            mock_getcwd.return_value = '/original/dir'
            
            success, output = self.manager._run_git_command(['status'], self.temp_dir)
            
            assert success is True
            mock_chdir.assert_has_calls([call(self.temp_dir), call('/original/dir')])
    
    @patch('subprocess.run')
    def test_run_git_command_timeout(self, mock_run):
        """Test Git command timeout handling"""
        mock_run.side_effect = subprocess.TimeoutExpired('git', 10)
        
        success, output = self.manager._run_git_command(['status'])
        
        assert success is False
        assert output == 'Command timed out'
    
    @patch('subprocess.run')
    def test_run_git_command_exception(self, mock_run):
        """Test Git command exception handling"""
        mock_run.side_effect = Exception('Test error')
        
        success, output = self.manager._run_git_command(['status'])
        
        assert success is False
        assert output == 'Test error'


class TestGitBranchOperations:
    """Test Git branch operation methods"""
    
    def setup_method(self):
        """Set up test environment"""
        self.manager = GitContextManager()
    
    @patch.object(GitContextManager, '_run_git_command')
    def test_get_current_branch_success(self, mock_run_git):
        """Test successful current branch retrieval"""
        mock_run_git.return_value = (True, 'feature/test-branch')
        
        branch = self.manager.get_current_branch('/repo')
        
        assert branch == 'feature/test-branch'
        mock_run_git.assert_called_once_with(['branch', '--show-current'], '/repo')
    
    @patch.object(GitContextManager, '_run_git_command')
    def test_get_current_branch_failure(self, mock_run_git):
        """Test failed current branch retrieval"""
        mock_run_git.return_value = (False, 'error')
        
        branch = self.manager.get_current_branch('/repo')
        
        assert branch == ""
    
    @patch.object(GitContextManager, '_run_git_command')
    def test_get_remote_tracking_branch_success(self, mock_run_git):
        """Test successful remote tracking branch retrieval"""
        mock_run_git.return_value = (True, 'refs/heads/main')
        
        remote_branch = self.manager.get_remote_tracking_branch('/repo', 'feature')
        
        assert remote_branch == 'main'
        mock_run_git.assert_called_once_with(
            ['config', '--get', 'branch.feature.merge'], '/repo'
        )
    
    @patch.object(GitContextManager, '_run_git_command')
    def test_get_remote_tracking_branch_failure(self, mock_run_git):
        """Test failed remote tracking branch retrieval"""
        mock_run_git.return_value = (False, 'error')
        
        remote_branch = self.manager.get_remote_tracking_branch('/repo', 'feature')
        
        assert remote_branch == ""
    
    @patch.object(GitContextManager, '_run_git_command')
    def test_get_remote_tracking_branch_no_refs_prefix(self, mock_run_git):
        """Test remote tracking branch without refs/heads/ prefix"""
        mock_run_git.return_value = (True, 'main')
        
        remote_branch = self.manager.get_remote_tracking_branch('/repo', 'feature')
        
        assert remote_branch == 'main'


class TestGitAheadBehindCount:
    """Test Git ahead/behind count functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.manager = GitContextManager()
    
    @patch.object(GitContextManager, '_run_git_command')
    def test_get_ahead_behind_count_success(self, mock_run_git):
        """Test successful ahead/behind count retrieval"""
        mock_run_git.return_value = (True, '2\t3')
        
        ahead, behind = self.manager.get_ahead_behind_count('/repo', 'feature', 'main')
        
        assert ahead == 3
        assert behind == 2
        mock_run_git.assert_called_once_with(
            ['rev-list', '--left-right', '--count', 'origin/main...feature'], '/repo'
        )
    
    @patch.object(GitContextManager, '_run_git_command')
    def test_get_ahead_behind_count_failure(self, mock_run_git):
        """Test failed ahead/behind count retrieval"""
        mock_run_git.return_value = (False, 'error')
        
        ahead, behind = self.manager.get_ahead_behind_count('/repo', 'feature', 'main')
        
        assert ahead == 0
        assert behind == 0
    
    @patch.object(GitContextManager, '_run_git_command')
    def test_get_ahead_behind_count_invalid_output(self, mock_run_git):
        """Test ahead/behind count with invalid output"""
        mock_run_git.return_value = (True, 'invalid output')
        
        ahead, behind = self.manager.get_ahead_behind_count('/repo', 'feature', 'main')
        
        assert ahead == 0
        assert behind == 0
    
    def test_get_ahead_behind_count_no_remote_branch(self):
        """Test ahead/behind count with no remote branch"""
        ahead, behind = self.manager.get_ahead_behind_count('/repo', 'feature', '')
        
        assert ahead == 0
        assert behind == 0


class TestGitRepositoryStatus:
    """Test Git repository status functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.manager = GitContextManager()
    
    @patch.object(GitContextManager, '_run_git_command')
    def test_get_repository_status_success(self, mock_run_git):
        """Test successful repository status retrieval"""
        status_output = """M  modified_file.py
A  added_file.py
D  deleted_file.py
 M unstaged_modified.py
 D unstaged_deleted.py
?? untracked_file.py
?? another_untracked.py"""
        
        mock_run_git.return_value = (True, status_output)
        
        status = self.manager.get_repository_status('/repo')
        
        assert status['staged_files'] == ['modified_file.py', 'added_file.py', 'deleted_file.py']
        assert status['unstaged_files'] == ['unstaged_modified.py', 'unstaged_deleted.py']
        assert status['untracked_files'] == ['untracked_file.py', 'another_untracked.py']
        assert status['has_staged_changes'] is True
        assert status['has_unstaged_changes'] is True
        assert status['has_untracked_files'] is True
    
    @patch.object(GitContextManager, '_run_git_command')
    def test_get_repository_status_clean(self, mock_run_git):
        """Test repository status with clean working directory"""
        mock_run_git.return_value = (True, '')
        
        status = self.manager.get_repository_status('/repo')
        
        assert status['staged_files'] == []
        assert status['unstaged_files'] == []
        assert status['untracked_files'] == []
        assert status['has_staged_changes'] is False
        assert status['has_unstaged_changes'] is False
        assert status['has_untracked_files'] is False
    
    @patch.object(GitContextManager, '_run_git_command')
    def test_get_repository_status_failure(self, mock_run_git):
        """Test failed repository status retrieval"""
        mock_run_git.return_value = (False, 'error')
        
        status = self.manager.get_repository_status('/repo')
        
        assert status['staged_files'] == []
        assert status['unstaged_files'] == []
        assert status['untracked_files'] == []
        assert status['has_staged_changes'] is False
        assert status['has_unstaged_changes'] is False
        assert status['has_untracked_files'] is False
    
    @patch.object(GitContextManager, '_run_git_command')
    def test_get_repository_status_complex_changes(self, mock_run_git):
        """Test repository status with complex change types"""
        status_output = """MM mixed_changes.py
R  renamed_file.py
C  copied_file.py
AM added_then_modified.py
 R renamed_unstaged.py"""
        
        mock_run_git.return_value = (True, status_output)
        
        status = self.manager.get_repository_status('/repo')
        
        # MM = staged modified + unstaged modified
        # R = renamed (staged)
        # C = copied (staged)
        # AM = added (staged) + modified (unstaged)
        # R = renamed (unstaged only)
        
        expected_staged = ['mixed_changes.py', 'renamed_file.py', 'copied_file.py', 'added_then_modified.py']
        expected_unstaged = ['mixed_changes.py', 'added_then_modified.py']
        
        assert status['staged_files'] == expected_staged
        assert status['unstaged_files'] == expected_unstaged


class TestGitMergeConflictDetection:
    """Test Git merge conflict detection"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = GitContextManager()
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_check_merge_conflict_true(self):
        """Test merge conflict detection when conflict exists"""
        # Create .git directory and MERGE_HEAD file
        git_dir = Path(self.temp_dir) / '.git'
        git_dir.mkdir()
        (git_dir / 'MERGE_HEAD').touch()
        
        in_conflict = self.manager.check_merge_conflict(self.temp_dir)
        assert in_conflict is True
    
    def test_check_merge_conflict_false(self):
        """Test merge conflict detection when no conflict exists"""
        # Create .git directory without MERGE_HEAD file
        git_dir = Path(self.temp_dir) / '.git'
        git_dir.mkdir()
        
        in_conflict = self.manager.check_merge_conflict(self.temp_dir)
        assert in_conflict is False
    
    def test_check_merge_conflict_no_git_dir(self):
        """Test merge conflict detection when no .git directory exists"""
        in_conflict = self.manager.check_merge_conflict(self.temp_dir)
        assert in_conflict is False


class TestGitRepositoryStateGeneration:
    """Test comprehensive Git repository state generation"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = GitContextManager()
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch.object(GitContextManager, 'find_git_repository')
    def test_get_repository_state_not_git_repo(self, mock_find_git):
        """Test repository state when not in Git repository"""
        mock_find_git.return_value = None
        
        state = self.manager.get_repository_state()
        
        assert state.is_git_repo is False
        assert state.current_branch == ""
        assert state.repository_root == ""
    
    @patch.object(GitContextManager, 'check_merge_conflict')
    @patch.object(GitContextManager, 'get_repository_status')
    @patch.object(GitContextManager, 'get_ahead_behind_count')
    @patch.object(GitContextManager, 'get_remote_tracking_branch')
    @patch.object(GitContextManager, 'get_current_branch')
    @patch.object(GitContextManager, 'find_git_repository')
    def test_get_repository_state_complete(self, mock_find_git, mock_get_branch, 
                                         mock_get_remote, mock_get_ahead_behind,
                                         mock_get_status, mock_check_conflict):
        """Test complete repository state generation"""
        # Setup mocks
        mock_find_git.return_value = '/repo'
        mock_get_branch.return_value = 'feature/test'
        mock_get_remote.return_value = 'main'
        mock_get_ahead_behind.return_value = (2, 1)
        mock_get_status.return_value = {
            'staged_files': ['file1.py'],
            'unstaged_files': ['file2.py'],
            'untracked_files': ['file3.py'],
            'has_staged_changes': True,
            'has_unstaged_changes': True,
            'has_untracked_files': True
        }
        mock_check_conflict.return_value = False
        
        state = self.manager.get_repository_state()
        
        assert state.is_git_repo is True
        assert state.current_branch == 'feature/test'
        assert state.remote_branch == 'main'
        assert state.ahead_commits == 2
        assert state.behind_commits == 1
        assert state.has_staged_changes is True
        assert state.has_unstaged_changes is True
        assert state.has_untracked_files is True
        assert state.in_merge_conflict is False
        assert state.staged_files == ['file1.py']
        assert state.unstaged_files == ['file2.py']
        assert state.untracked_files == ['file3.py']
        assert state.repository_root == '/repo'
    
    @patch.object(GitContextManager, 'find_git_repository')
    def test_get_repository_state_caching(self, mock_find_git):
        """Test repository state caching mechanism"""
        mock_find_git.return_value = None
        
        # First call should populate cache
        state1 = self.manager.get_repository_state()
        assert self.manager._cached_state is not None
        
        # Second call should return cached version
        state2 = self.manager.get_repository_state()
        assert state1 is state2  # Should be same object
    
    @patch.object(GitContextManager, 'find_git_repository')
    def test_get_repository_state_force_refresh(self, mock_find_git):
        """Test repository state with forced refresh"""
        mock_find_git.return_value = None
        
        state1 = self.manager.get_repository_state()
        state2 = self.manager.get_repository_state(force_refresh=True)
        
        # Should be different objects (new instance created)
        assert state1 is not state2
    
    @patch.object(GitContextManager, 'find_git_repository')
    def test_get_repository_state_cache_expiry(self, mock_find_git):
        """Test repository state cache expiry"""
        mock_find_git.return_value = None
        
        # Set very short cache time
        self.manager._cache_ttl = 1  # Use integer instead of float
        
        state1 = self.manager.get_repository_state()
        time.sleep(0.2)  # Wait for cache to expire
        state2 = self.manager.get_repository_state()
        
        # Should be different objects due to cache expiry
        assert state1 is not state2


class TestGitCommandSuggestions:
    """Test Git command suggestions"""
    
    def setup_method(self):
        """Set up test environment"""
        self.manager = GitContextManager()
    
    def test_suggest_git_command_status(self):
        """Test Git status command suggestion"""
        state = GitRepositoryState(is_git_repo=True)
        
        suggestion = self.manager.suggest_git_command('status', state)
        
        assert suggestion is not None
        assert suggestion['command'] == 'git status'
        assert suggestion['confidence'] == 0.95
        assert suggestion['context_aware'] is True
        assert suggestion['git_context'] is True
    
    def test_suggest_git_command_commit_with_staged_changes(self):
        """Test commit command suggestion with staged changes"""
        state = GitRepositoryState(
            is_git_repo=True,
            has_staged_changes=True,
            has_unstaged_changes=False
        )
        
        suggestion = self.manager.suggest_git_command('commit', state)
        
        assert suggestion is not None
        assert 'git commit -m "Update: commit staged changes"' == suggestion['command']
        assert suggestion['confidence'] == 0.9
    
    def test_suggest_git_command_commit_with_unstaged_changes(self):
        """Test commit command suggestion with unstaged changes"""
        state = GitRepositoryState(
            is_git_repo=True,
            has_staged_changes=False,
            has_unstaged_changes=True
        )
        
        suggestion = self.manager.suggest_git_command('commit', state)
        
        assert suggestion is not None
        assert 'git add . && git commit -m "Update: staged and commit changes"' == suggestion['command']
    
    def test_suggest_git_command_push_with_remote_branch(self):
        """Test push command suggestion with remote branch"""
        state = GitRepositoryState(
            is_git_repo=True,
            current_branch='feature/test',
            remote_branch='main'
        )
        
        suggestion = self.manager.suggest_git_command('push', state)
        
        assert suggestion is not None
        assert suggestion['command'] == 'git push origin feature/test'
    
    def test_suggest_git_command_push_without_remote_branch(self):
        """Test push command suggestion without remote branch"""
        state = GitRepositoryState(
            is_git_repo=True,
            current_branch='feature/test',
            remote_branch=''
        )
        
        suggestion = self.manager.suggest_git_command('push', state)
        
        assert suggestion is not None
        assert suggestion['command'] == 'git push -u origin feature/test'
    
    def test_suggest_git_command_pull_with_remote_branch(self):
        """Test pull command suggestion with remote branch"""
        state = GitRepositoryState(
            is_git_repo=True,
            remote_branch='main'
        )
        
        suggestion = self.manager.suggest_git_command('pull', state)
        
        assert suggestion is not None
        assert suggestion['command'] == 'git pull origin main'
    
    def test_suggest_git_command_pull_without_remote_branch(self):
        """Test pull command suggestion without remote branch"""
        state = GitRepositoryState(
            is_git_repo=True,
            remote_branch=''
        )
        
        suggestion = self.manager.suggest_git_command('pull', state)
        
        assert suggestion is not None
        assert suggestion['command'] == 'git pull'
    
    def test_suggest_git_command_branch_switch_clean(self):
        """Test branch switch command suggestion with clean working directory"""
        state = GitRepositoryState(
            is_git_repo=True,
            has_staged_changes=False,
            has_unstaged_changes=False
        )
        
        suggestion = self.manager.suggest_git_command('switch to main', state)
        
        assert suggestion is not None
        assert suggestion['command'] == 'git checkout main'
    
    def test_suggest_git_command_branch_switch_with_changes(self):
        """Test branch switch command suggestion with uncommitted changes"""
        state = GitRepositoryState(
            is_git_repo=True,
            has_staged_changes=True,
            has_unstaged_changes=True
        )
        
        suggestion = self.manager.suggest_git_command('checkout main', state)
        
        assert suggestion is not None
        assert suggestion['command'] == 'git stash && git checkout main'
    
    def test_suggest_git_command_not_git_repo(self):
        """Test command suggestion when not in Git repository"""
        state = GitRepositoryState(is_git_repo=False)
        
        suggestion = self.manager.suggest_git_command('status', state)
        
        assert suggestion is None
    
    def test_suggest_git_command_no_match(self):
        """Test command suggestion with no matching patterns"""
        state = GitRepositoryState(is_git_repo=True)
        
        suggestion = self.manager.suggest_git_command('unknown command', state)
        
        assert suggestion is None
    
    @patch.object(GitContextManager, 'get_repository_state')
    def test_suggest_git_command_without_explicit_state(self, mock_get_state):
        """Test command suggestion without providing explicit state"""
        mock_state = GitRepositoryState(is_git_repo=True)
        mock_get_state.return_value = mock_state
        
        suggestion = self.manager.suggest_git_command('status')
        
        mock_get_state.assert_called_once()
        assert suggestion is not None


class TestGitUtilityMethods:
    """Test Git utility methods"""
    
    def setup_method(self):
        """Set up test environment"""
        self.manager = GitContextManager()
    
    def test_get_smart_commit_command_staged_changes_only(self):
        """Test smart commit command with staged changes only"""
        state = GitRepositoryState(
            has_staged_changes=True,
            has_unstaged_changes=False
        )
        
        command = self.manager._get_smart_commit_command(state)
        assert command == 'git commit -m "Update: commit staged changes"'
    
    def test_get_smart_commit_command_unstaged_changes_only(self):
        """Test smart commit command with unstaged changes only"""
        state = GitRepositoryState(
            has_staged_changes=False,
            has_unstaged_changes=True
        )
        
        command = self.manager._get_smart_commit_command(state)
        assert command == 'git add . && git commit -m "Update: staged and commit changes"'
    
    def test_get_smart_commit_command_no_changes(self):
        """Test smart commit command with no changes"""
        state = GitRepositoryState(
            has_staged_changes=False,
            has_unstaged_changes=False
        )
        
        command = self.manager._get_smart_commit_command(state)
        assert command == 'git add . && git commit -m "Update: stage and commit all changes"'
    
    def test_get_safe_branch_switch_command_clean(self):
        """Test safe branch switch with clean working directory"""
        state = GitRepositoryState(
            has_staged_changes=False,
            has_unstaged_changes=False
        )
        
        command = self.manager._get_safe_branch_switch_command('main', state)
        assert command == 'git checkout main'
    
    def test_get_safe_branch_switch_command_with_changes(self):
        """Test safe branch switch with uncommitted changes"""
        state = GitRepositoryState(
            has_staged_changes=True,
            has_unstaged_changes=False
        )
        
        command = self.manager._get_safe_branch_switch_command('main', state)
        assert command == 'git stash && git checkout main'
        
        # Test with unstaged changes
        state.has_staged_changes = False
        state.has_unstaged_changes = True
        
        command = self.manager._get_safe_branch_switch_command('develop', state)
        assert command == 'git stash && git checkout develop'
    
    def test_get_smart_push_command_with_remote_branch(self):
        """Test smart push command with existing remote branch"""
        state = GitRepositoryState(
            current_branch='feature/test',
            remote_branch='main'
        )
        
        command = self.manager._get_smart_push_command(state)
        assert command == 'git push origin feature/test'
    
    def test_get_smart_push_command_without_remote_branch(self):
        """Test smart push command without remote branch"""
        state = GitRepositoryState(
            current_branch='feature/test',
            remote_branch=''
        )
        
        command = self.manager._get_smart_push_command(state)
        assert command == 'git push -u origin feature/test'


class TestCommitMessageGeneration:
    """Test intelligent commit message generation"""
    
    def setup_method(self):
        """Set up test environment"""
        self.manager = GitContextManager()
    
    def test_generate_commit_message_no_files(self):
        """Test commit message generation with no files"""
        state = GitRepositoryState(
            staged_files=[],
            unstaged_files=[]
        )
        
        message = self.manager.generate_commit_message(state)
        assert message == "Update: general changes"
    
    def test_generate_commit_message_test_files(self):
        """Test commit message generation with test files"""
        state = GitRepositoryState(
            staged_files=['test_app.py', 'tests/test_feature.py'],
            unstaged_files=['unit_test.py']
        )
        
        message = self.manager.generate_commit_message(state)
        assert message == "test: update test files"
    
    def test_generate_commit_message_documentation_files(self):
        """Test commit message generation with documentation files"""
        state = GitRepositoryState(
            staged_files=['README.md', 'docs/guide.txt'],
            unstaged_files=['CHANGELOG.rst']
        )
        
        message = self.manager.generate_commit_message(state)
        assert message == "docs: update documentation"
    
    def test_generate_commit_message_config_files(self):
        """Test commit message generation with config files"""
        state = GitRepositoryState(
            staged_files=['config.json', 'settings.yml'],
            unstaged_files=['app.toml', 'setup.ini']
        )
        
        message = self.manager.generate_commit_message(state)
        assert message == "config: update configuration files"
    
    def test_generate_commit_message_code_files(self):
        """Test commit message generation with code files"""
        state = GitRepositoryState(
            staged_files=['app.py', 'feature.js'],
            unstaged_files=['utils.ts', 'main.java', 'helper.cpp']
        )
        
        message = self.manager.generate_commit_message(state)
        assert message == "feat: update code implementation"
    
    def test_generate_commit_message_mixed_files(self):
        """Test commit message generation with mixed file types (priority: tests > docs > config > code)"""
        state = GitRepositoryState(
            staged_files=['app.py', 'test_app.py', 'README.md'],
            unstaged_files=['config.json']
        )
        
        message = self.manager.generate_commit_message(state)
        assert message == "test: update test files"  # Tests have highest priority
    
    def test_generate_commit_message_other_files(self):
        """Test commit message generation with other file types"""
        state = GitRepositoryState(
            staged_files=['data.csv', 'image.png'],
            unstaged_files=['notes.txt']  # notes.txt is detected as docs
        )
        
        message = self.manager.generate_commit_message(state)
        assert message == "docs: update documentation"
    
    def test_generate_commit_message_single_other_file(self):
        """Test commit message generation with single other file"""
        state = GitRepositoryState(
            staged_files=['data.csv'],
            unstaged_files=[]
        )
        
        message = self.manager.generate_commit_message(state)
        assert message == "update: modify 1 file"


class TestGitSafetyWarnings:
    """Test Git safety warnings"""
    
    def setup_method(self):
        """Set up test environment"""
        self.manager = GitContextManager()
    
    def test_git_safety_warnings_force_operation(self):
        """Test safety warnings for force operations"""
        state = GitRepositoryState()
        
        warnings = self.manager.get_git_safety_warnings('git push --force', state)
        assert len(warnings) == 1
        assert "Force operation detected" in warnings[0]
        
        warnings = self.manager.get_git_safety_warnings('git reset -f', state)
        assert len(warnings) == 1
        assert "Force operation detected" in warnings[0]
    
    def test_git_safety_warnings_hard_reset(self):
        """Test safety warnings for hard reset"""
        state = GitRepositoryState()
        
        warnings = self.manager.get_git_safety_warnings('git reset --hard HEAD~1', state)
        assert len(warnings) == 1
        assert "Hard reset will permanently delete" in warnings[0]
    
    def test_git_safety_warnings_push_with_unstaged_changes(self):
        """Test safety warnings for push with unstaged changes"""
        state = GitRepositoryState(has_unstaged_changes=True)
        
        warnings = self.manager.get_git_safety_warnings('git push origin main', state)
        assert len(warnings) == 1
        assert "unstaged changes that won't be pushed" in warnings[0]
    
    def test_git_safety_warnings_checkout_with_changes(self):
        """Test safety warnings for checkout with uncommitted changes"""
        state = GitRepositoryState(has_unstaged_changes=True, has_staged_changes=True)
        
        warnings = self.manager.get_git_safety_warnings('git checkout main', state)
        assert len(warnings) == 1
        assert "Consider stashing changes" in warnings[0]
    
    def test_git_safety_warnings_merge_during_conflict(self):
        """Test safety warnings for merge during conflict"""
        state = GitRepositoryState(in_merge_conflict=True)
        
        warnings = self.manager.get_git_safety_warnings('git merge feature', state)
        assert len(warnings) == 1
        assert "Repository is in merge conflict state" in warnings[0]
    
    def test_git_safety_warnings_multiple_warnings(self):
        """Test multiple safety warnings"""
        state = GitRepositoryState(
            has_unstaged_changes=True,
            in_merge_conflict=True
        )
        
        warnings = self.manager.get_git_safety_warnings('git push --force', state)
        assert len(warnings) == 2
        assert any("Force operation detected" in w for w in warnings)
        assert any("unstaged changes that won't be pushed" in w for w in warnings)
    
    def test_git_safety_warnings_clean_operation(self):
        """Test no warnings for clean operations"""
        state = GitRepositoryState()
        
        warnings = self.manager.get_git_safety_warnings('git status', state)
        assert len(warnings) == 0
        
        warnings = self.manager.get_git_safety_warnings('git log', state)
        assert len(warnings) == 0


if __name__ == '__main__':
    # Run basic functionality tests
    print("=== Testing Git Context Manager ===")
    
    # Test individual components
    test_cases = [
        TestGitRepositoryState(),
        TestGitContextManagerInitialization(),
        TestGitRepositoryFinding(),
        TestGitCommandExecution(),
        TestGitBranchOperations(),
        TestGitAheadBehindCount(),
        TestGitRepositoryStatus(),
        TestGitMergeConflictDetection(),
        TestGitRepositoryStateGeneration(),
        TestGitCommandSuggestions(),
        TestGitUtilityMethods(),
        TestCommitMessageGeneration(),
        TestGitSafetyWarnings()
    ]
    
    for test_case in test_cases:
        test_case.setup_method()
        print(f"✓ {test_case.__class__.__name__} setup complete")
    
    print("=== Git Context Tests Ready ===")