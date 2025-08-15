"""
Comprehensive test coverage for Git Context module (currently 0% coverage)
Critical for Git repository awareness and intelligent Git command suggestions
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import subprocess
from pathlib import Path
from nlcli.git_context import GitContext


class TestGitContextComprehensive(unittest.TestCase):
    """Comprehensive test cases for GitContext"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.git_context = GitContext()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test GitContext initialization"""
        context = GitContext()
        self.assertIsNotNone(context)
    
    def test_is_git_repository_true(self):
        """Test detection of Git repository"""
        # Create a mock Git repository
        git_dir = os.path.join(self.temp_dir, '.git')
        os.makedirs(git_dir)
        
        with patch('os.getcwd', return_value=self.temp_dir):
            result = self.git_context.is_git_repository()
            self.assertTrue(result)
    
    def test_is_git_repository_false(self):
        """Test detection when not in Git repository"""
        with patch('os.getcwd', return_value=self.temp_dir):
            result = self.git_context.is_git_repository()
            self.assertFalse(result)
    
    def test_get_current_branch(self):
        """Test getting current Git branch"""
        mock_output = "main\n"
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = mock_output
            mock_run.return_value.returncode = 0
            
            branch = self.git_context.get_current_branch()
            self.assertEqual(branch, "main")
    
    def test_get_current_branch_detached(self):
        """Test getting branch in detached HEAD state"""
        mock_output = "HEAD detached at abc1234\n"
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = mock_output
            mock_run.return_value.returncode = 0
            
            branch = self.git_context.get_current_branch()
            self.assertIn("detached", branch.lower())
    
    def test_get_git_status(self):
        """Test getting Git status information"""
        mock_status = """M  modified_file.py
A  new_file.txt
D  deleted_file.md
?? untracked_file.log
"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = mock_status
            mock_run.return_value.returncode = 0
            
            status = self.git_context.get_git_status()
            self.assertIsInstance(status, dict)
            self.assertIn('modified', status)
            self.assertIn('added', status)
            self.assertIn('deleted', status)
            self.assertIn('untracked', status)
    
    def test_has_uncommitted_changes(self):
        """Test detection of uncommitted changes"""
        mock_status = "M  file.py\n"
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = mock_status
            mock_run.return_value.returncode = 0
            
            has_changes = self.git_context.has_uncommitted_changes()
            self.assertTrue(has_changes)
    
    def test_has_no_uncommitted_changes(self):
        """Test detection when no uncommitted changes"""
        mock_status = ""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = mock_status
            mock_run.return_value.returncode = 0
            
            has_changes = self.git_context.has_uncommitted_changes()
            self.assertFalse(has_changes)
    
    def test_get_recent_commits(self):
        """Test getting recent commit history"""
        mock_log = """abc1234 Fix bug in user authentication
def5678 Add new feature for file processing
ghi9012 Update documentation
"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = mock_log
            mock_run.return_value.returncode = 0
            
            commits = self.git_context.get_recent_commits(3)
            self.assertIsInstance(commits, list)
            self.assertEqual(len(commits), 3)
            self.assertIn('abc1234', commits[0])
    
    def test_get_remote_info(self):
        """Test getting remote repository information"""
        mock_remotes = "origin\thttps://github.com/user/repo.git (fetch)\n"
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = mock_remotes
            mock_run.return_value.returncode = 0
            
            remotes = self.git_context.get_remote_info()
            self.assertIsInstance(remotes, dict)
            self.assertIn('origin', remotes)
    
    def test_has_merge_conflicts(self):
        """Test detection of merge conflicts"""
        mock_status = """UU conflicted_file.py
AA both_added.txt
"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = mock_status
            mock_run.return_value.returncode = 0
            
            has_conflicts = self.git_context.has_merge_conflicts()
            self.assertTrue(has_conflicts)
    
    def test_get_stash_list(self):
        """Test getting Git stash list"""
        mock_stash = """stash@{0}: WIP on main: abc1234 Latest commit
stash@{1}: On feature: def5678 Previous work
"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = mock_stash
            mock_run.return_value.returncode = 0
            
            stashes = self.git_context.get_stash_list()
            self.assertIsInstance(stashes, list)
            self.assertEqual(len(stashes), 2)
    
    def test_get_branch_list(self):
        """Test getting list of branches"""
        mock_branches = """  feature/new-ui
* main
  develop
  hotfix/urgent-fix
"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = mock_branches
            mock_run.return_value.returncode = 0
            
            branches = self.git_context.get_branch_list()
            self.assertIsInstance(branches, dict)
            self.assertIn('current', branches)
            self.assertIn('all', branches)
            self.assertEqual(branches['current'], 'main')
    
    def test_is_behind_remote(self):
        """Test checking if local branch is behind remote"""
        mock_output = "1\t0\torigin/main\n"  # 1 behind, 0 ahead
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = mock_output
            mock_run.return_value.returncode = 0
            
            is_behind = self.git_context.is_behind_remote()
            self.assertTrue(is_behind)
    
    def test_is_ahead_of_remote(self):
        """Test checking if local branch is ahead of remote"""
        mock_output = "0\t2\torigin/main\n"  # 0 behind, 2 ahead
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = mock_output
            mock_run.return_value.returncode = 0
            
            is_ahead = self.git_context.is_ahead_of_remote()
            self.assertTrue(is_ahead)
    
    def test_suggest_git_commands(self):
        """Test Git command suggestions based on context"""
        # Test suggestions when there are uncommitted changes
        with patch.object(self.git_context, 'has_uncommitted_changes', return_value=True):
            suggestions = self.git_context.suggest_git_commands("commit my changes")
            self.assertIsInstance(suggestions, list)
            self.assertTrue(any('commit' in cmd for cmd in suggestions))
    
    def test_suggest_commands_for_conflicts(self):
        """Test command suggestions when there are merge conflicts"""
        with patch.object(self.git_context, 'has_merge_conflicts', return_value=True):
            suggestions = self.git_context.suggest_git_commands("resolve conflicts")
            self.assertIsInstance(suggestions, list)
            self.assertTrue(any('merge' in cmd or 'rebase' in cmd for cmd in suggestions))
    
    def test_get_file_changes(self):
        """Test getting changes for specific files"""
        mock_diff = """@@ -1,3 +1,4 @@
 line1
+new line
 line2
 line3
"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = mock_diff
            mock_run.return_value.returncode = 0
            
            changes = self.git_context.get_file_changes('test.py')
            self.assertIsInstance(changes, str)
            self.assertIn('new line', changes)
    
    def test_get_repository_info(self):
        """Test getting comprehensive repository information"""
        with patch.object(self.git_context, 'is_git_repository', return_value=True), \
             patch.object(self.git_context, 'get_current_branch', return_value='main'), \
             patch.object(self.git_context, 'has_uncommitted_changes', return_value=True), \
             patch.object(self.git_context, 'get_remote_info', return_value={'origin': 'https://github.com/user/repo.git'}):
            
            info = self.git_context.get_repository_info()
            self.assertIsInstance(info, dict)
            self.assertIn('is_git_repo', info)
            self.assertIn('current_branch', info)
            self.assertIn('has_changes', info)
            self.assertIn('remotes', info)
    
    def test_validate_git_command(self):
        """Test validation of Git commands for safety"""
        safe_commands = [
            "git status",
            "git log",
            "git diff",
            "git branch",
            "git show",
            "git fetch"
        ]
        
        dangerous_commands = [
            "git reset --hard HEAD~10",
            "git push --force",
            "git clean -fd",
            "git reflog expire --all"
        ]
        
        for cmd in safe_commands:
            with self.subTest(command=cmd):
                is_safe = self.git_context.validate_git_command(cmd)
                self.assertTrue(is_safe, f"Command '{cmd}' should be safe")
        
        for cmd in dangerous_commands:
            with self.subTest(command=cmd):
                is_safe = self.git_context.validate_git_command(cmd)
                self.assertFalse(is_safe, f"Command '{cmd}' should be dangerous")
    
    def test_get_commit_suggestions(self):
        """Test getting commit message suggestions"""
        mock_status = """M  src/main.py
A  tests/test_new.py
D  old_file.txt
"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = mock_status
            mock_run.return_value.returncode = 0
            
            suggestions = self.git_context.get_commit_suggestions()
            self.assertIsInstance(suggestions, list)
            self.assertGreater(len(suggestions), 0)
    
    def test_get_workflow_suggestions(self):
        """Test getting workflow suggestions based on repository state"""
        # Test feature branch workflow
        with patch.object(self.git_context, 'get_current_branch', return_value='feature/new-feature'):
            suggestions = self.git_context.get_workflow_suggestions()
            self.assertIsInstance(suggestions, list)
            self.assertTrue(any('merge' in s or 'pull request' in s for s in suggestions))
    
    def test_detect_git_hooks(self):
        """Test detection of Git hooks"""
        hooks_dir = os.path.join(self.temp_dir, '.git', 'hooks')
        os.makedirs(hooks_dir, exist_ok=True)
        
        # Create a pre-commit hook
        hook_file = os.path.join(hooks_dir, 'pre-commit')
        with open(hook_file, 'w') as f:
            f.write('#!/bin/bash\necho "Running tests..."')
        os.chmod(hook_file, 0o755)
        
        with patch('os.getcwd', return_value=self.temp_dir):
            hooks = self.git_context.detect_git_hooks()
            self.assertIsInstance(hooks, list)
            self.assertIn('pre-commit', hooks)
    
    def test_get_ignored_files(self):
        """Test getting list of ignored files"""
        gitignore_content = """*.pyc
__pycache__/
.env
node_modules/
"""
        gitignore_path = os.path.join(self.temp_dir, '.gitignore')
        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content)
        
        with patch('os.getcwd', return_value=self.temp_dir):
            ignored = self.git_context.get_ignored_patterns()
            self.assertIsInstance(ignored, list)
            self.assertIn('*.pyc', ignored)
            self.assertIn('__pycache__/', ignored)
    
    def test_analyze_commit_history(self):
        """Test analysis of commit history patterns"""
        mock_log = """John Doe	2023-12-01	Fix bug in authentication
Jane Smith	2023-11-30	Add new feature
John Doe	2023-11-29	Update documentation
"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = mock_log
            mock_run.return_value.returncode = 0
            
            analysis = self.git_context.analyze_commit_history(10)
            self.assertIsInstance(analysis, dict)
            self.assertIn('contributors', analysis)
            self.assertIn('recent_activity', analysis)
    
    def test_get_submodule_info(self):
        """Test getting submodule information"""
        mock_submodules = """160000 commit abc1234 0	external/library
160000 commit def5678 0	vendor/plugin
"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = mock_submodules
            mock_run.return_value.returncode = 0
            
            submodules = self.git_context.get_submodule_info()
            self.assertIsInstance(submodules, list)
            self.assertEqual(len(submodules), 2)
    
    def test_error_handling_git_not_installed(self):
        """Test error handling when Git is not installed"""
        with patch('subprocess.run', side_effect=FileNotFoundError("git not found")):
            result = self.git_context.is_git_repository()
            self.assertFalse(result)
    
    def test_error_handling_git_command_failure(self):
        """Test error handling when Git commands fail"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "fatal: not a git repository"
            
            result = self.git_context.get_current_branch()
            self.assertIsNone(result)
    
    def test_performance_caching(self):
        """Test performance optimization through caching"""
        # First call should execute Git command
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = "main\n"
            mock_run.return_value.returncode = 0
            
            branch1 = self.git_context.get_current_branch(use_cache=True)
            branch2 = self.git_context.get_current_branch(use_cache=True)
            
            # Should only call subprocess once due to caching
            self.assertEqual(mock_run.call_count, 1)
            self.assertEqual(branch1, branch2)
    
    def test_get_tag_info(self):
        """Test getting Git tag information"""
        mock_tags = """v1.0.0
v1.1.0
v2.0.0-beta
"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = mock_tags
            mock_run.return_value.returncode = 0
            
            tags = self.git_context.get_tag_info()
            self.assertIsInstance(tags, list)
            self.assertIn('v1.0.0', tags)
            self.assertIn('v2.0.0-beta', tags)
    
    def test_detect_large_files(self):
        """Test detection of large files in repository"""
        mock_output = """1048576	large_file.bin
2097152	huge_dataset.csv
"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = mock_output
            mock_run.return_value.returncode = 0
            
            large_files = self.git_context.detect_large_files(threshold_mb=1)
            self.assertIsInstance(large_files, list)
            self.assertEqual(len(large_files), 2)
    
    def test_get_security_suggestions(self):
        """Test getting security-related suggestions"""
        # Test when sensitive files are detected
        mock_status = """A  .env
M  config/database.yml
?? keys/private.key
"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = mock_status
            mock_run.return_value.returncode = 0
            
            suggestions = self.git_context.get_security_suggestions()
            self.assertIsInstance(suggestions, list)
            # Should suggest adding sensitive files to .gitignore
            self.assertTrue(any('gitignore' in s.lower() for s in suggestions))
    
    def test_branch_naming_validation(self):
        """Test validation of branch naming conventions"""
        valid_names = [
            "feature/user-authentication",
            "bugfix/login-error",
            "hotfix/security-patch",
            "release/v1.2.0"
        ]
        
        invalid_names = [
            "feature",  # Too generic
            "fix",      # Too short
            "FEATURE/NEW-STUFF",  # Wrong case
            "feature@new#feature"  # Invalid characters
        ]
        
        for name in valid_names:
            with self.subTest(branch=name):
                is_valid = self.git_context.validate_branch_name(name)
                self.assertTrue(is_valid, f"Branch name '{name}' should be valid")
        
        for name in invalid_names:
            with self.subTest(branch=name):
                is_valid = self.git_context.validate_branch_name(name)
                self.assertFalse(is_valid, f"Branch name '{name}' should be invalid")
    
    def test_integration_with_other_tools(self):
        """Test integration with other development tools"""
        # Test CI/CD detection
        ci_files = ['.github/workflows/ci.yml', '.gitlab-ci.yml', 'Jenkinsfile']
        for ci_file in ci_files:
            ci_path = os.path.join(self.temp_dir, ci_file)
            os.makedirs(os.path.dirname(ci_path), exist_ok=True)
            with open(ci_path, 'w') as f:
                f.write('# CI configuration')
        
        with patch('os.getcwd', return_value=self.temp_dir):
            ci_info = self.git_context.detect_ci_integration()
            self.assertIsInstance(ci_info, dict)
            self.assertIn('has_ci', ci_info)
            self.assertTrue(ci_info['has_ci'])


if __name__ == '__main__':
    unittest.main()