"""
CLI commands for command history management
"""

import os
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from ..ui.interactive_input import InteractiveInputHandler

console = Console()

@click.group()
def history():
    """Command history management"""
    pass

@history.command()
@click.option('--limit', '-l', default=20, help='Number of commands to show')
@click.pass_context
def show(ctx, limit):
    """Show recent command history"""
    
    history_manager = ctx.obj['history']
    commands = history_manager.get_recent_commands(limit)
    
    if not commands:
        console.print("[yellow]No command history found.[/yellow]")
        return
    
    # Create table for command history
    table = Table(show_header=True, header_style="bold magenta", title=f"Recent Commands (Last {len(commands)})")
    table.add_column("ID", style="dim", width=6)
    table.add_column("Natural Language", style="cyan", max_width=40)
    table.add_column("Command", style="white", max_width=40)
    table.add_column("Status", style="white", width=10)
    table.add_column("Time", style="dim", width=16)
    
    for cmd in commands:
        # Format timestamp
        import datetime
        timestamp = datetime.datetime.fromisoformat(cmd['timestamp']).strftime("%m-%d %H:%M")
        
        # Format status
        status = "✓ Success" if cmd['success'] else "✗ Failed"
        status_style = "green" if cmd['success'] else "red"
        
        # Truncate long text
        nl_text = cmd['natural_language'][:37] + "..." if len(cmd['natural_language']) > 40 else cmd['natural_language']
        cmd_text = cmd['command'][:37] + "..." if len(cmd['command']) > 40 else cmd['command']
        
        table.add_row(
            str(cmd['id']),
            nl_text,
            cmd_text,
            f"[{status_style}]{status}[/{status_style}]",
            timestamp
        )
    
    console.print(table)

@history.command()
@click.argument('query')
@click.option('--limit', '-l', default=10, help='Number of results to show')
@click.pass_context
def search(ctx, query, limit):
    """Search command history"""
    
    history_manager = ctx.obj['history']
    commands = history_manager.search_commands(query, limit)
    
    if not commands:
        console.print(f"[yellow]No commands found matching '{query}'[/yellow]")
        return
    
    console.print(f"[bold]Search Results for '{query}'[/bold]")
    
    # Create table for search results
    table = Table(show_header=True, header_style="bold green")
    table.add_column("ID", style="dim", width=6)
    table.add_column("Natural Language", style="cyan", max_width=35)
    table.add_column("Command", style="white", max_width=35)
    table.add_column("Status", style="white", width=10)
    table.add_column("Time", style="dim", width=16)
    
    for cmd in commands:
        # Format timestamp
        import datetime
        timestamp = datetime.datetime.fromisoformat(cmd['timestamp']).strftime("%m-%d %H:%M")
        
        # Format status
        status = "✓ Success" if cmd['success'] else "✗ Failed"
        status_style = "green" if cmd['success'] else "red"
        
        # Highlight search term
        nl_text = cmd['natural_language']
        cmd_text = cmd['command']
        
        # Truncate if needed
        if len(nl_text) > 32:
            nl_text = nl_text[:29] + "..."
        if len(cmd_text) > 32:
            cmd_text = cmd_text[:29] + "..."
        
        table.add_row(
            str(cmd['id']),
            nl_text,
            cmd_text,
            f"[{status_style}]{status}[/{status_style}]",
            timestamp
        )
    
    console.print(table)

@history.command()
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def clear(ctx, confirm):
    """Clear command history"""
    
    if not confirm:
        from rich.prompt import Confirm
        if not Confirm.ask("Are you sure you want to clear all command history?", default=False):
            console.print("[yellow]Operation cancelled.[/yellow]")
            return
    
    history_manager = ctx.obj['history']
    
    try:
        # Clear database history
        history_manager.clear_command_history()
        
        # Clear input history file
        history_file = os.path.join(os.path.expanduser('~/.nlcli'), 'input_history')
        if os.path.exists(history_file):
            os.remove(history_file)
        
        console.print("[green]✓ Command history cleared successfully[/green]")
        
    except Exception as e:
        console.print(f"[red]Error clearing history: {e}[/red]")

@history.command()
@click.pass_context
def stats(ctx):
    """Show command history statistics"""
    
    history_manager = ctx.obj['history']
    
    try:
        # Get all commands for statistics
        all_commands = history_manager.get_recent_commands(1000)
        
        if not all_commands:
            console.print("[yellow]No command history found.[/yellow]")
            return
        
        # Calculate statistics
        total_commands = len(all_commands)
        successful_commands = sum(1 for cmd in all_commands if cmd['success'])
        failed_commands = total_commands - successful_commands
        success_rate = (successful_commands / total_commands) * 100
        
        # Most common commands
        command_counts = {}
        nl_counts = {}
        
        for cmd in all_commands:
            command = cmd['command']
            nl = cmd['natural_language']
            
            command_counts[command] = command_counts.get(command, 0) + 1
            nl_counts[nl] = nl_counts.get(nl, 0) + 1
        
        # Get top commands
        top_commands = sorted(command_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_nl = sorted(nl_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Display statistics
        stats_table = Table(show_header=True, header_style="bold magenta", title="Command History Statistics")
        stats_table.add_column("Metric", style="cyan", width=20)
        stats_table.add_column("Value", style="white")
        
        stats_table.add_row("Total Commands", str(total_commands))
        stats_table.add_row("Successful", f"{successful_commands} ({success_rate:.1f}%)")
        stats_table.add_row("Failed", f"{failed_commands} ({100-success_rate:.1f}%)")
        
        console.print(stats_table)
        
        # Top commands
        if top_commands:
            console.print("\n[bold]Most Used Commands[/bold]")
            cmd_table = Table(show_header=True, header_style="bold green")
            cmd_table.add_column("Command", style="cyan", max_width=40)
            cmd_table.add_column("Count", style="white", width=8)
            
            for command, count in top_commands:
                cmd_text = command[:37] + "..." if len(command) > 40 else command
                cmd_table.add_row(cmd_text, str(count))
            
            console.print(cmd_table)
        
        # Top natural language
        if top_nl:
            console.print("\n[bold]Most Used Natural Language Phrases[/bold]")
            nl_table = Table(show_header=True, header_style="bold blue")
            nl_table.add_column("Natural Language", style="cyan", max_width=40)
            nl_table.add_column("Count", style="white", width=8)
            
            for nl, count in top_nl:
                nl_text = nl[:37] + "..." if len(nl) > 40 else nl
                nl_table.add_row(nl_text, str(count))
            
            console.print(nl_table)
        
    except Exception as e:
        console.print(f"[red]Error calculating statistics: {e}[/red]")

@history.command()
@click.argument('command_id', type=int)
@click.pass_context
def repeat(ctx, command_id):
    """Repeat a command from history by ID"""
    
    history_manager = ctx.obj['history']
    
    try:
        # Get the specific command
        commands = history_manager.get_recent_commands(1000)
        target_command = None
        
        for cmd in commands:
            if cmd['id'] == command_id:
                target_command = cmd
                break
        
        if not target_command:
            console.print(f"[red]Command with ID {command_id} not found[/red]")
            return
        
        console.print(f"[bold]Repeating command #{command_id}:[/bold]")
        console.print(f"Natural Language: [cyan]{target_command['natural_language']}[/cyan]")
        console.print(f"Command: [white]{target_command['command']}[/white]")
        
        from rich.prompt import Confirm
        if Confirm.ask("Execute this command?", default=True):
            # Execute the command
            executor = ctx.obj['executor']
            result = executor.execute(target_command['command'])
            
            # Store in history
            history_manager.add_command(
                target_command['natural_language'], 
                target_command['command'], 
                target_command['explanation'], 
                result['success']
            )
            
            # Display result
            if result['success']:
                console.print(f"[green]✓ Command executed successfully[/green]")
                if result['output']:
                    console.print(Panel(result['output'], title="Output", border_style="green"))
            else:
                console.print(f"[red]✗ Command failed[/red]")
                if result['error']:
                    console.print(Panel(result['error'], title="Error", border_style="red"))
        else:
            console.print("[yellow]Command cancelled.[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error repeating command: {e}[/red]")

@history.command()
@click.pass_context
def export(ctx):
    """Export command history to file"""
    
    history_manager = ctx.obj['history']
    
    try:
        commands = history_manager.get_recent_commands(1000)
        
        if not commands:
            console.print("[yellow]No command history to export.[/yellow]")
            return
        
        # Export to CSV format
        export_file = os.path.expanduser('~/.nlcli/history_export.csv')
        
        with open(export_file, 'w') as f:
            # Write header
            f.write("ID,Timestamp,Natural Language,Command,Explanation,Success,Platform\n")
            
            # Write data
            for cmd in commands:
                # Escape quotes in CSV
                nl = cmd['natural_language'].replace('"', '""')
                command = cmd['command'].replace('"', '""')
                explanation = cmd.get('explanation', '').replace('"', '""')
                platform = cmd.get('platform', 'unknown')
                
                f.write(f'{cmd["id"]},"{cmd["timestamp"]}","{nl}","{command}","{explanation}",{cmd["success"]},"{platform}"\n')
        
        console.print(f"[green]✓ Exported {len(commands)} commands to {export_file}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error exporting history: {e}[/red]")