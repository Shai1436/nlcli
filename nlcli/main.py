"""
Main CLI interface for Natural Language CLI Tool
"""

import click
import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.text import Text
from rich.table import Table

from .ai_translator import AITranslator
from .history_manager import HistoryManager
from .safety_checker import SafetyChecker
from .config_manager import ConfigManager
from .command_executor import CommandExecutor
from .utils import setup_logging, get_platform_info

console = Console()
logger = setup_logging()

@click.group(invoke_without_command=True)
@click.option('--config-path', help='Path to configuration file')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, config_path, verbose):
    """Natural Language CLI - Translate natural language to OS commands"""
    
    # Initialize context
    ctx.ensure_object(dict)
    
    # Setup logging level
    if verbose:
        logger.setLevel('DEBUG')
    
    # Initialize components
    config = ConfigManager(config_path)
    ctx.obj['config'] = config
    ctx.obj['history'] = HistoryManager(config.get_db_path())
    ctx.obj['ai_translator'] = AITranslator(config.get_openai_key())
    ctx.obj['safety_checker'] = SafetyChecker(config.get_safety_level())
    ctx.obj['executor'] = CommandExecutor()
    
    # If no subcommand provided, start interactive mode
    if ctx.invoked_subcommand is None:
        interactive_mode(ctx.obj)

def interactive_mode(components):
    """Interactive mode for natural language command translation"""
    
    console.print(Panel.fit(
        "[bold green]Natural Language CLI[/bold green]\n"
        "Type your command in natural language, or 'quit' to exit\n"
        "Use 'history' to view command history, 'help' for more options",
        title="Welcome"
    ))
    
    history = components['history']
    ai_translator = components['ai_translator']
    safety_checker = components['safety_checker']
    executor = components['executor']
    
    while True:
        try:
            # Get user input
            user_input = console.input("\n[bold blue]→[/bold blue] ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'q']:
                console.print("[green]Goodbye![/green]")
                break
                
            if user_input.lower() == 'history':
                show_history(history)
                continue
                
            if user_input.lower() in ['help', 'h']:
                show_help()
                continue
                
            if user_input.lower() == 'clear':
                console.clear()
                continue
            
            # Translate natural language to command
            console.print("[yellow]Translating...[/yellow]")
            
            try:
                translation_result = ai_translator.translate(user_input)
                
                if not translation_result:
                    console.print("[red]Could not translate the command. Please try rephrasing.[/red]")
                    continue
                
                command = translation_result['command']
                explanation = translation_result['explanation']
                confidence = translation_result.get('confidence', 0.8)
                
                # Display command and explanation
                display_translation(command, explanation, confidence)
                
                # Safety check
                safety_result = safety_checker.check_command(command)
                
                if not safety_result['safe']:
                    console.print(f"[red]⚠️  Safety Warning: {safety_result['reason']}[/red]")
                    if not Confirm.ask("Do you want to proceed anyway?", default=False):
                        console.print("[yellow]Command cancelled.[/yellow]")
                        continue
                
                # Auto-execute read-only commands, confirm others
                is_read_only = safety_checker.is_read_only_command(command)
                if not is_read_only and not Confirm.ask(f"Execute this command?", default=True):
                    console.print("[yellow]Command cancelled.[/yellow]")
                    continue
                
                # Execute command
                console.print("[green]Executing...[/green]")
                result = executor.execute(command)
                
                # Store in history
                history.add_command(user_input, command, explanation, result['success'])
                
                # Display result
                display_execution_result(result)
                
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")
                logger.error(f"Error in interactive mode: {str(e)}")
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'quit' to exit.[/yellow]")
        except EOFError:
            console.print("\n[green]Goodbye![/green]")
            break

def display_translation(command, explanation, confidence):
    """Display the translated command with explanation"""
    
    # Create table for command details
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Command", style="cyan", no_wrap=True)
    table.add_column("Explanation", style="white")
    table.add_column("Confidence", style="green")
    
    confidence_display = f"{confidence:.0%}" if confidence else "Unknown"
    table.add_row(command, explanation, confidence_display)
    
    console.print(table)

def display_execution_result(result):
    """Display command execution result"""
    
    if result['success']:
        console.print(f"[green]✓ Command executed successfully[/green]")
        if result['output']:
            console.print(Panel(result['output'], title="Output", border_style="green"))
    else:
        console.print(f"[red]✗ Command failed[/red]")
        if result['error']:
            console.print(Panel(result['error'], title="Error", border_style="red"))

def show_history(history):
    """Display command history"""
    
    commands = history.get_recent_commands(10)
    
    if not commands:
        console.print("[yellow]No command history found.[/yellow]")
        return
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=6)
    table.add_column("Natural Language", style="cyan")
    table.add_column("Command", style="white")
    table.add_column("Status", style="green")
    table.add_column("Date", style="dim")
    
    for cmd in commands:
        status = "✓" if cmd['success'] else "✗"
        status_style = "green" if cmd['success'] else "red"
        table.add_row(
            str(cmd['id']),
            cmd['natural_language'][:50] + "..." if len(cmd['natural_language']) > 50 else cmd['natural_language'],
            cmd['command'][:50] + "..." if len(cmd['command']) > 50 else cmd['command'],
            f"[{status_style}]{status}[/{status_style}]",
            cmd['timestamp']
        )
    
    console.print(table)

def show_help():
    """Display help information"""
    
    help_text = """
[bold]Available Commands:[/bold]
• Type any natural language command
• [cyan]history[/cyan] - Show command history
• [cyan]clear[/cyan] - Clear the screen
• [cyan]help[/cyan] - Show this help
• [cyan]quit[/cyan] - Exit the application

[bold]Examples:[/bold]
• "list all files in the current directory"
• "create a new folder called projects"
• "show disk usage"
• "find all python files"
• "compress the documents folder"
    """
    
    console.print(Panel(help_text, title="Help", border_style="blue"))

@cli.command()
@click.argument('query')
@click.option('--execute', '-e', is_flag=True, help='Execute without confirmation')
@click.option('--explain-only', is_flag=True, help='Only show explanation, do not execute')
@click.pass_obj
def translate(obj, query, execute, explain_only):
    """Translate a single natural language query to OS command"""
    
    ai_translator = obj['ai_translator']
    safety_checker = obj['safety_checker']
    executor = obj['executor']
    history = obj['history']
    
    try:
        # Translate command
        result = ai_translator.translate(query)
        
        if not result:
            console.print("[red]Could not translate the command.[/red]")
            return
        
        command = result['command']
        explanation = result['explanation']
        confidence = result.get('confidence', 0.8)
        
        # Display translation
        display_translation(command, explanation, confidence)
        
        if explain_only:
            return
        
        # Safety check
        safety_result = safety_checker.check_command(command)
        
        if not safety_result['safe']:
            console.print(f"[red]⚠️  Safety Warning: {safety_result['reason']}[/red]")
            if not execute and not Confirm.ask("Do you want to proceed anyway?", default=False):
                return
        
        # Execute if requested
        if execute or Confirm.ask("Execute this command?", default=False):
            exec_result = executor.execute(command)
            history.add_command(query, command, explanation, exec_result['success'])
            display_execution_result(exec_result)
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")

@cli.command()
@click.option('--limit', '-l', default=20, help='Number of commands to show')
@click.pass_obj
def history(obj, limit):
    """Show command history"""
    
    history_manager = obj['history']
    commands = history_manager.get_recent_commands(limit)
    
    if not commands:
        console.print("[yellow]No command history found.[/yellow]")
        return
    
    show_history(history_manager)

@cli.command()
@click.pass_obj
def config(obj):
    """Show current configuration"""
    
    config_manager = obj['config']
    platform_info = get_platform_info()
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Config Path", config_manager.config_path)
    table.add_row("Database Path", config_manager.get_db_path())
    table.add_row("Safety Level", config_manager.get_safety_level())
    table.add_row("Platform", platform_info['platform'])
    table.add_row("Python Version", platform_info['python_version'])
    table.add_row("OpenAI Key", "Set" if config_manager.get_openai_key() else "Not Set")
    
    console.print(table)

if __name__ == '__main__':
    cli()
