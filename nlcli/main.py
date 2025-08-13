"""
Main CLI interface for Natural Language CLI Tool
"""

import click
import os
import sys
import time
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
from .output_formatter import OutputFormatter
from .context_cli import context
from .history_cli import history as history_cli
from .filter_cli import filter as filter_cli
from .interactive_input import create_input_handler, get_input_capabilities
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
    ctx.obj['ai_translator'] = AITranslator(
        api_key=config.get_openai_key(),
        enable_cache=config.get('performance', 'enable_cache', fallback='true').lower() == 'true'
    )
    ctx.obj['safety_checker'] = SafetyChecker(config.get_safety_level())
    ctx.obj['executor'] = CommandExecutor()
    ctx.obj['formatter'] = OutputFormatter()
    
    # If no subcommand provided, start interactive mode
    if ctx.invoked_subcommand is None:
        interactive_mode(ctx.obj)

def interactive_mode(obj):
    """Interactive mode for natural language command translation"""
    
    # Show enhanced welcome banner
    formatter = obj['formatter']
    formatter.format_welcome_banner()
    
    history = obj['history']
    ai_translator = obj['ai_translator']
    safety_checker = obj['safety_checker']
    executor = obj['executor']
    config = obj['config']
    
    # Create input handler with history support
    history_file = os.path.join(os.path.expanduser('~/.nlcli'), 'input_history')
    
    with create_input_handler(history_file) as input_handler:
        # Load existing natural language history into input handler
        recent_nl_commands = history.get_recent_natural_language_commands(50)
        for nl_command in recent_nl_commands:
            input_handler.add_to_history(nl_command)
        
        while True:
            try:
                # Get user input with styled prompt (blue chevron style like AskCLI)
                user_input = input_handler.get_input("[bold blue]❯[/bold blue] ").strip()
            
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
                start_time = time.time()
                console.print("[yellow]Translating...[/yellow]")
                
                try:
                    api_timeout = float(obj['config'].get('performance', 'api_timeout', fallback='8.0'))
                    translation_result = ai_translator.translate(user_input, timeout=api_timeout)
                    
                    # Show performance info
                    elapsed = time.time() - start_time
                    if translation_result:
                        if translation_result.get('direct'):
                            console.print(f"[dim blue]🚀 Direct execution ({elapsed:.3f}s)[/dim blue]")
                        elif translation_result.get('context_aware'):
                            context_type = translation_result.get('context_type', 'unknown')
                            console.print(f"[dim cyan]🎯 Context-aware ({context_type}) ({elapsed:.3f}s)[/dim cyan]")
                        elif translation_result.get('instant'):
                            console.print(f"[dim green]⚡ Instant match ({elapsed:.3f}s)[/dim green]")
                        elif translation_result.get('cached'):
                            console.print(f"[dim green]📋 Cached result ({elapsed:.3f}s)[/dim green]")
                        else:
                            console.print(f"[dim yellow]🤖 AI translation ({elapsed:.3f}s)[/dim yellow]")
                    
                    if not translation_result:
                        console.print("[red]Could not translate the command. Please try rephrasing.[/red]")
                        continue
                    
                    command = translation_result['command']
                    explanation = translation_result['explanation']
                    confidence = translation_result.get('confidence', 0.8)
                    
                    # Display enhanced command result
                    result_data = {
                        'command': command,
                        'explanation': explanation,
                        'confidence': confidence,
                        'source': translation_result.get('source', 'ai_translation')
                    }
                    formatter.format_command_result(result_data, elapsed)
                    
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
                    
                    # Update context with command execution
                    ai_translator.context_manager.update_command_history(command, result['success'])
                    
                    # Display enhanced results
                    if result.get('output'):
                        formatter.format_command_output(
                            result['output'], 
                            command,
                            result['success']
                        )
                    
                    if not result['success']:
                        formatter.format_error(f"Command failed with exit code {result.get('exit_code', 'unknown')}")
                    else:
                        console.print("[green]✓ Command executed successfully[/green]")
                    
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
    """Display enhanced command history using formatter"""
    
    commands = history.get_recent_commands(10)
    
    if not commands:
        console.print("[yellow]No command history found.[/yellow]")
        return
    
    # Create the object structure that formatter expects
    obj = {'formatter': OutputFormatter()}
    formatter = obj['formatter']
    
    # Convert to expected format
    history_data = []
    for cmd in commands:
        history_data.append({
            'id': cmd['id'],
            'natural_language': cmd['natural_language'],
            'command': cmd['command'],
            'success': cmd['success'],
            'timestamp': cmd.get('timestamp', '')
        })
    
    formatter.format_history_table(history_data)

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

@cli.command()
@click.pass_obj
def performance(obj):
    """Show performance statistics and cache info"""
    
    ai_translator = obj['ai_translator']
    
    if not ai_translator.cache_manager:
        console.print("[yellow]Cache is disabled[/yellow]")
        return
    
    # Get cache statistics
    stats = ai_translator.cache_manager.get_cache_stats()
    popular = ai_translator.cache_manager.get_popular_commands(5)
    
    # Performance statistics table
    perf_table = Table(show_header=True, header_style="bold magenta", title="Performance Statistics")
    perf_table.add_column("Metric", style="cyan")
    perf_table.add_column("Value", style="white")
    
    perf_table.add_row("Cached Translations", str(stats.get('total_entries', 0)))
    perf_table.add_row("Total Cache Uses", str(stats.get('total_uses', 0)))
    perf_table.add_row("Average Uses per Command", str(stats.get('average_uses', 0)))
    perf_table.add_row("Cache Hit Potential", stats.get('cache_hit_potential', '0%'))
    perf_table.add_row("Instant Patterns Available", str(len(ai_translator.instant_patterns)))
    
    console.print(perf_table)
    
    # Popular commands table
    if popular:
        console.print()
        pop_table = Table(show_header=True, header_style="bold green", title="Most Used Commands")
        pop_table.add_column("Natural Language", style="cyan")
        pop_table.add_column("Command", style="white")
        pop_table.add_column("Uses", style="yellow")
        
        for cmd in popular:
            pop_table.add_row(
                cmd['natural_language'][:40] + "..." if len(cmd['natural_language']) > 40 else cmd['natural_language'],
                cmd['command'],
                str(cmd['use_count'])
            )
        
        console.print(pop_table)

# Add additional command groups to CLI
cli.add_command(context)
cli.add_command(history_cli)
cli.add_command(filter_cli)

if __name__ == '__main__':
    cli()
