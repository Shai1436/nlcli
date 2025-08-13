"""
CLI commands for context management
"""

import os
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from .context_manager import ContextManager

console = Console()

@click.group()
def context():
    """Context awareness commands"""
    pass

@context.command()
@click.pass_context
def status(ctx):
    """Show current context information"""
    
    config_dir = os.path.expanduser('~/.nlcli')
    context_manager = ContextManager(str(config_dir))
    
    context_info = context_manager.get_context_info()
    
    # Current environment table
    env_table = Table(show_header=True, header_style="bold magenta", title="Current Context")
    env_table.add_column("Property", style="cyan")
    env_table.add_column("Value", style="white")
    
    env_table.add_row("Current Directory", context_info['current_directory'])
    
    git_info = context_info['git_context']
    if git_info.get('is_repo'):
        env_table.add_row("Git Repository", "Yes")
        env_table.add_row("Git Branch", git_info.get('branch', 'unknown'))
        env_table.add_row("Has Changes", "Yes" if git_info.get('has_changes') else "No")
    else:
        env_table.add_row("Git Repository", "No")
    
    # Project types
    project_types = context_info['environment'].get('project_types', [])
    env_table.add_row("Project Types", ', '.join(project_types) if project_types else "None detected")
    
    # Python environment
    python_env = context_info['environment'].get('python', {})
    if python_env.get('virtual_env'):
        env_table.add_row("Python Virtual Env", python_env['virtual_env'])
    elif python_env.get('conda_env'):
        env_table.add_row("Conda Environment", python_env['conda_env'])
    
    env_table.add_row("Available Shortcuts", str(context_info['available_shortcuts']))
    
    console.print(env_table)
    
    # Recent directories
    recent_dirs = context_info['recent_directories']
    if recent_dirs:
        console.print()
        dir_table = Table(show_header=True, header_style="bold green", title="Recent Directories")
        dir_table.add_column("Directory", style="cyan")
        
        for directory in recent_dirs:
            dir_name = directory if len(directory) < 60 else f"...{directory[-57:]}"
            dir_table.add_row(dir_name)
        
        console.print(dir_table)

@context.command()
@click.pass_context
def shortcuts(ctx):
    """Show available shortcuts"""
    
    config_dir = os.path.expanduser('~/.nlcli')
    context_manager = ContextManager(str(config_dir))
    
    # Group shortcuts by category
    shortcut_categories = {
        'Navigation': ['..', '...', '....', '-', '~'],
        'Git': [k for k in context_manager.shortcuts.keys() if k.startswith('g') and len(k) <= 3],
        'File Operations': ['l', 'll', 'la', 'lt', 'lh'],
        'System': ['df', 'du', 'free', 'psg', 'k9'],
        'Text Processing': ['grep', 'egrep', 'fgrep'],
        'Archives': ['targz', 'untargz']
    }
    
    for category, shortcuts in shortcut_categories.items():
        if shortcuts:
            console.print(f"\n[bold {['magenta', 'green', 'blue', 'yellow', 'cyan', 'red'][list(shortcut_categories.keys()).index(category) % 6]}]{category} Shortcuts[/]")
            
            table = Table(show_header=True, header_style="dim")
            table.add_column("Shortcut", style="cyan", width=12)
            table.add_column("Command", style="white")
            table.add_column("Description", style="dim")
            
            for shortcut in shortcuts:
                if shortcut in context_manager.shortcuts:
                    command = context_manager.shortcuts[shortcut]
                    description = _get_shortcut_description(shortcut, command)
                    table.add_row(shortcut, command, description)
            
            console.print(table)

def _get_shortcut_description(shortcut: str, command: str) -> str:
    """Get description for a shortcut"""
    
    descriptions = {
        '..': 'Go up one directory',
        '...': 'Go up two directories',
        '....': 'Go up three directories',
        '-': 'Go to previous directory',
        '~': 'Go to home directory',
        'g': 'Git command alias',
        'ga': 'Stage files for commit',
        'gaa': 'Stage all files',
        'gc': 'Create commit',
        'gcm': 'Commit with message',
        'gco': 'Checkout branch/file',
        'gd': 'Show git diff',
        'gl': 'Show git log',
        'gp': 'Push to remote',
        'gpl': 'Pull from remote',
        'gs': 'Show git status',
        'gb': 'List/create branches',
        'l': 'List files detailed',
        'll': 'List files long format',
        'la': 'List all files',
        'lt': 'List by time',
        'lh': 'List human readable',
        'df': 'Show disk space',
        'du': 'Show directory size',
        'free': 'Show memory usage',
        'psg': 'Search processes',
        'k9': 'Force kill process',
        'grep': 'Search text (colored)',
        'targz': 'Create tar.gz archive',
        'untargz': 'Extract tar.gz archive'
    }
    
    return descriptions.get(shortcut, 'Custom shortcut')

@context.command()
@click.argument('shortcut')
@click.argument('command')
@click.pass_context
def add_shortcut(ctx, shortcut, command):
    """Add a custom shortcut"""
    
    config_dir = os.path.expanduser('~/.nlcli')
    context_manager = ContextManager(str(config_dir))
    
    # Load current shortcuts
    try:
        import json
        custom_shortcuts = {}
        if context_manager.shortcuts_file.exists():
            with open(context_manager.shortcuts_file, 'r') as f:
                custom_shortcuts = json.load(f)
        
        # Add new shortcut
        custom_shortcuts[shortcut] = command
        
        # Save shortcuts
        with open(context_manager.shortcuts_file, 'w') as f:
            json.dump(custom_shortcuts, f, indent=2)
        
        console.print(f"[green]✓ Added shortcut: {shortcut} → {command}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error adding shortcut: {e}[/red]")

@context.command()
@click.argument('shortcut')
@click.pass_context
def remove_shortcut(ctx, shortcut):
    """Remove a custom shortcut"""
    
    config_dir = os.path.expanduser('~/.nlcli')
    context_manager = ContextManager(str(config_dir))
    
    try:
        import json
        custom_shortcuts = {}
        if context_manager.shortcuts_file.exists():
            with open(context_manager.shortcuts_file, 'r') as f:
                custom_shortcuts = json.load(f)
        
        if shortcut in custom_shortcuts:
            del custom_shortcuts[shortcut]
            
            # Save shortcuts
            with open(context_manager.shortcuts_file, 'w') as f:
                json.dump(custom_shortcuts, f, indent=2)
            
            console.print(f"[green]✓ Removed shortcut: {shortcut}[/green]")
        else:
            console.print(f"[yellow]Shortcut '{shortcut}' not found[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error removing shortcut: {e}[/red]")

@context.command()
@click.pass_context
def suggestions(ctx):
    """Show context-aware suggestions for current environment"""
    
    config_dir = os.path.expanduser('~/.nlcli')
    context_manager = ContextManager(str(config_dir))
    
    # Get suggestions for common scenarios
    test_phrases = [
        "show status",
        "install dependencies", 
        "run tests",
        "commit changes",
        "list files",
        "go to project"
    ]
    
    console.print("[bold]Context-Aware Suggestions[/bold]")
    console.print("Based on your current environment:\n")
    
    for phrase in test_phrases:
        suggestions = context_manager.get_context_suggestions(phrase)
        
        if suggestions:
            console.print(f"[cyan]'{phrase}'[/cyan]")
            
            # Show top 3 suggestions
            for i, suggestion in enumerate(suggestions[:3]):
                confidence = suggestion['confidence']
                context_type = suggestion['context_type']
                source = suggestion['source']
                
                console.print(f"  {i+1}. [white]{suggestion['command']}[/white]")
                console.print(f"     [dim]{suggestion['explanation']} ({confidence:.0%} confidence)[/dim]")
                console.print(f"     [dim]Source: {source} ({context_type})[/dim]")
            
            console.print()