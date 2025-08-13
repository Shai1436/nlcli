"""
Account Manager for cross-account functionality using dot files
"""

import os
import json
import configparser
from pathlib import Path
from typing import Dict, List, Optional, Any
from .utils import setup_logging

logger = setup_logging()

class AccountManager:
    """Manages multiple user accounts and configurations"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize account manager
        
        Args:
            config_dir: Custom configuration directory path
        """
        
        self.config_dir = Path(config_dir) if config_dir else Path.home() / '.nlcli'
        self.accounts_dir = self.config_dir / 'accounts'
        self.shared_dir = self.config_dir / 'shared'
        self.global_config_path = self.config_dir / 'global.ini'
        self.current_account_file = self.config_dir / '.current_account'
        
        self._ensure_directories()
        self._load_global_config()
    
    def _ensure_directories(self):
        """Ensure all necessary directories exist"""
        
        directories = [
            self.config_dir,
            self.accounts_dir,
            self.shared_dir,
            self.shared_dir / 'templates',
            self.shared_dir / 'patterns'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_global_config(self):
        """Load global configuration"""
        
        self.global_config = configparser.ConfigParser()
        
        # Default global settings
        defaults = {
            'accounts': {
                'default_account': 'default',
                'auto_switch': 'false',
                'shared_cache': 'true',
                'shared_patterns': 'true'
            },
            'security': {
                'require_account_auth': 'false',
                'session_timeout': '0',  # 0 = no timeout
                'encrypt_sensitive_data': 'false'
            },
            'sync': {
                'enabled': 'false',
                'sync_history': 'false',
                'sync_cache': 'true',
                'sync_patterns': 'true'
            }
        }
        
        if self.global_config_path.exists():
            self.global_config.read(self.global_config_path)
        else:
            # Create default global config
            for section, settings in defaults.items():
                self.global_config.add_section(section)
                for key, value in settings.items():
                    self.global_config.set(section, key, value)
            
            self._save_global_config()
    
    def _save_global_config(self):
        """Save global configuration"""
        
        try:
            with open(self.global_config_path, 'w') as f:
                self.global_config.write(f)
        except Exception as e:
            logger.error(f"Error saving global config: {e}")
    
    def create_account(self, account_name: str, config: Optional[Dict] = None) -> bool:
        """
        Create a new user account
        
        Args:
            account_name: Name of the account to create
            config: Optional initial configuration
            
        Returns:
            True if account was created successfully
        """
        
        if not account_name or account_name.startswith('.'):
            logger.error("Invalid account name")
            return False
        
        account_dir = self.accounts_dir / account_name
        
        if account_dir.exists():
            logger.warning(f"Account '{account_name}' already exists")
            return False
        
        try:
            # Create account directory structure
            account_dir.mkdir(parents=True)
            (account_dir / 'config').mkdir()
            (account_dir / 'data').mkdir()
            (account_dir / 'cache').mkdir()
            (account_dir / 'logs').mkdir()
            
            # Create account metadata
            metadata = {
                'name': account_name,
                'created': str(Path.ctime(account_dir)),
                'last_used': None,
                'version': '1.0.0',
                'settings': config or {}
            }
            
            with open(account_dir / 'account.json', 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Create account-specific config
            account_config = configparser.ConfigParser()
            account_config.read_dict({
                'general': {
                    'account_name': account_name,
                    'safety_level': config.get('safety_level', 'medium') if config else 'medium',
                    'auto_confirm_read_only': 'true',
                    'max_history_items': '1000'
                },
                'ai': {
                    'model': 'gpt-4o-mini',
                    'temperature': '0.1',
                    'max_tokens': '300',
                    'timeout': '10'
                },
                'performance': {
                    'enable_cache': 'true',
                    'enable_instant_patterns': 'true',
                    'api_timeout': '8.0',
                    'use_shared_cache': 'true'
                }
            })
            
            with open(account_dir / 'config' / 'config.ini', 'w') as f:
                account_config.write(f)
            
            logger.info(f"Created account: {account_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating account '{account_name}': {e}")
            return False
    
    def list_accounts(self) -> List[Dict[str, Any]]:
        """
        List all available accounts
        
        Returns:
            List of account information dictionaries
        """
        
        accounts = []
        
        try:
            for account_dir in self.accounts_dir.iterdir():
                if account_dir.is_dir() and not account_dir.name.startswith('.'):
                    metadata_file = account_dir / 'account.json'
                    
                    if metadata_file.exists():
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                            accounts.append(metadata)
                    else:
                        # Legacy account without metadata
                        accounts.append({
                            'name': account_dir.name,
                            'created': 'unknown',
                            'last_used': None,
                            'version': 'legacy'
                        })
        
        except Exception as e:
            logger.error(f"Error listing accounts: {e}")
        
        return accounts
    
    def switch_account(self, account_name: str) -> bool:
        """
        Switch to a different account
        
        Args:
            account_name: Name of account to switch to
            
        Returns:
            True if switch was successful
        """
        
        account_dir = self.accounts_dir / account_name
        
        if not account_dir.exists():
            logger.error(f"Account '{account_name}' does not exist")
            return False
        
        try:
            # Update current account file
            with open(self.current_account_file, 'w') as f:
                f.write(account_name)
            
            # Update last used timestamp
            metadata_file = account_dir / 'account.json'
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                metadata['last_used'] = str(Path.ctime(Path.cwd()))
                
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
            
            logger.info(f"Switched to account: {account_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error switching to account '{account_name}': {e}")
            return False
    
    def get_current_account(self) -> str:
        """
        Get the name of the currently active account
        
        Returns:
            Current account name
        """
        
        try:
            if self.current_account_file.exists():
                with open(self.current_account_file, 'r') as f:
                    account_name = f.read().strip()
                
                # Verify account still exists
                if (self.accounts_dir / account_name).exists():
                    return account_name
        
        except Exception as e:
            logger.error(f"Error getting current account: {e}")
        
        # Fall back to default account
        default_account = self.global_config.get('accounts', 'default_account', fallback='default')
        
        # Create default account if it doesn't exist
        if not (self.accounts_dir / default_account).exists():
            self.create_account(default_account)
            self.switch_account(default_account)
        
        return default_account
    
    def get_account_config_path(self, account_name: Optional[str] = None) -> str:
        """
        Get the configuration file path for an account
        
        Args:
            account_name: Account name (uses current account if None)
            
        Returns:
            Path to account's config file
        """
        
        if not account_name:
            account_name = self.get_current_account()
        
        return str(self.accounts_dir / account_name / 'config' / 'config.ini')
    
    def get_account_data_dir(self, account_name: Optional[str] = None) -> str:
        """
        Get the data directory path for an account
        
        Args:
            account_name: Account name (uses current account if None)
            
        Returns:
            Path to account's data directory
        """
        
        if not account_name:
            account_name = self.get_current_account()
        
        return str(self.accounts_dir / account_name / 'data')
    
    def get_shared_cache_dir(self) -> str:
        """
        Get the shared cache directory path
        
        Returns:
            Path to shared cache directory
        """
        
        return str(self.shared_dir / 'cache')
    
    def delete_account(self, account_name: str, force: bool = False) -> bool:
        """
        Delete an account and all its data
        
        Args:
            account_name: Name of account to delete
            force: Force deletion without confirmation
            
        Returns:
            True if account was deleted successfully
        """
        
        if account_name == 'default' and not force:
            logger.error("Cannot delete default account without force flag")
            return False
        
        account_dir = self.accounts_dir / account_name
        
        if not account_dir.exists():
            logger.warning(f"Account '{account_name}' does not exist")
            return True
        
        try:
            import shutil
            shutil.rmtree(account_dir)
            
            # Switch to default account if current account was deleted
            current = self.get_current_account()
            if current == account_name:
                self.switch_account('default')
            
            logger.info(f"Deleted account: {account_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting account '{account_name}': {e}")
            return False
    
    def export_account(self, account_name: str, export_path: str) -> bool:
        """
        Export account configuration and data
        
        Args:
            account_name: Name of account to export
            export_path: Path to export file
            
        Returns:
            True if export was successful
        """
        
        account_dir = self.accounts_dir / account_name
        
        if not account_dir.exists():
            logger.error(f"Account '{account_name}' does not exist")
            return False
        
        try:
            import tarfile
            
            with tarfile.open(export_path, 'w:gz') as tar:
                tar.add(account_dir, arcname=account_name)
            
            logger.info(f"Exported account '{account_name}' to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting account '{account_name}': {e}")
            return False
    
    def import_account(self, import_path: str, account_name: Optional[str] = None) -> bool:
        """
        Import account from exported file
        
        Args:
            import_path: Path to import file
            account_name: Name for imported account (auto-detect if None)
            
        Returns:
            True if import was successful
        """
        
        try:
            import tarfile
            
            with tarfile.open(import_path, 'r:gz') as tar:
                # Extract to temporary location first
                import tempfile
                with tempfile.TemporaryDirectory() as temp_dir:
                    tar.extractall(temp_dir)
                    
                    # Find the account directory
                    extracted_dirs = [d for d in Path(temp_dir).iterdir() if d.is_dir()]
                    
                    if not extracted_dirs:
                        logger.error("No account directory found in import file")
                        return False
                    
                    source_dir = extracted_dirs[0]
                    imported_name = account_name or source_dir.name
                    
                    # Copy to accounts directory
                    import shutil
                    target_dir = self.accounts_dir / imported_name
                    
                    if target_dir.exists():
                        logger.error(f"Account '{imported_name}' already exists")
                        return False
                    
                    shutil.copytree(source_dir, target_dir)
            
            logger.info(f"Imported account: {imported_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error importing account: {e}")
            return False