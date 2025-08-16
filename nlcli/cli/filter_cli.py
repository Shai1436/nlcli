"""
CLI commands for command filter management
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

@click.group()
def filter():
    """Command filter management"""
    pass

@filter.command()
@click.pass_context
def stats(ctx):
    """Show command filter statistics"""
    
    ai_translator = ctx.obj['ai_translator']
    command_filter = ai_translator.command_filter
    
    stats = command_filter.get_statistics()
    
    # Main statistics table
    stats_table = Table(show_header=True, header_style="bold magenta", title="Command Filter Statistics")
    stats_table.add_column("Metric", style="cyan", width=25)
    stats_table.add_column("Value", style="white")
    
    stats_table.add_row("Platform", stats['platform'].title())
    stats_table.add_row("Direct Commands", str(stats['total_direct_commands']))
    stats_table.add_row("Commands with Args", str(stats['total_commands_with_args']))
    stats_table.add_row("Total Available", str(stats['total_available']))
    
    console.print(stats_table)
    
    # Categories breakdown
    console.print("\n[bold]Command Categories[/bold]")
    cat_table = Table(show_header=True, header_style="bold green")
    cat_table.add_column("Category", style="cyan", width=20)
    cat_table.add_column("Count", style="white", width=8)
    
    for category, count in stats['categories'].items():
        cat_table.add_row(category.replace('_', ' ').title(), str(count))
    
    console.print(cat_table)

@filter.command()
@click.option('--category', help='Filter by category (navigation, file_ops, system, etc.)')
@click.option('--limit', '-l', default=20, help='Number of commands to show')
@click.pass_context
def list(ctx, category, limit):
    """List available direct commands"""
    
    ai_translator = ctx.obj['ai_translator']
    command_filter = ai_translator.command_filter
    
    # Get all direct commands
    all_commands = {}
    all_commands.update(command_filter.direct_commands)
    all_commands.update(command_filter.direct_commands_with_args)
    
    # Filter by category if specified
    if category:
        category_filters = {
            'navigation': ['ls', 'pwd', 'cd'],
            'file_ops': ['cat', 'cp', 'mv', 'rm', 'mkdir', 'touch'],
            'system': ['ps', 'top', 'df', 'du', 'free', 'uptime', 'whoami', 'date'],
            'network': ['ping', 'curl', 'wget'],
            'text': ['grep', 'sort', 'uniq', 'wc', 'head', 'tail'],
            'git': ['git status', 'git log', 'git diff', 'git branch'],
            'archives': ['tar', 'zip', 'unzip', 'gzip'],
        }
        
        if category in category_filters:
            filtered_commands = {}
            for cmd in category_filters[category]:
                if cmd in all_commands:
                    filtered_commands[cmd] = all_commands[cmd]
                # Also check for commands starting with the category command
                for full_cmd in all_commands:
                    if full_cmd.startswith(cmd + ' '):
                        filtered_commands[full_cmd] = all_commands[full_cmd]
            all_commands = filtered_commands
        else:
            console.print(f"[red]Unknown category: {category}[/red]")
            console.print("Available categories: navigation, file_ops, system, network, text, git, archives")
            return
    
    # Limit results
    commands = sorted(all_commands.items())[:limit]
    
    if not commands:
        console.print("[yellow]No commands found.[/yellow]")
        return
    
    # Display commands table
    title = f"Direct Commands"
    if category:
        title += f" ({category})"
    if len(commands) < len(all_commands):
        title += f" (showing {len(commands)} of {len(all_commands)})"
    
    table = Table(show_header=True, header_style="bold magenta", title=title)
    table.add_column("Command", style="cyan", max_width=25)
    table.add_column("Explanation", style="white", max_width=50)
    table.add_column("Confidence", style="green", width=10)
    table.add_column("Type", style="dim", width=10)
    
    for cmd, details in commands:
        confidence = f"{details['confidence']:.0%}"
        cmd_type = "Custom" if details.get('custom') else "Built-in"
        
        # Truncate long explanations
        explanation = details['explanation']
        if len(explanation) > 47:
            explanation = explanation[:44] + "..."
        
        table.add_row(cmd, explanation, confidence, cmd_type)
    
    console.print(table)

@filter.command()
@click.argument('query')
@click.option('--limit', '-l', default=10, help='Number of suggestions to show')
@click.pass_context
def suggest(ctx, query, limit):
    """Get command suggestions for partial input"""
    
    ai_translator = ctx.obj['ai_translator']
    command_filter = ai_translator.command_filter
    
    suggestions = command_filter.get_command_suggestions(query)
    
    if not suggestions:
        console.print(f"[yellow]No suggestions found for '{query}'[/yellow]")
        return
    
    console.print(f"[bold]Suggestions for '{query}'[/bold]")
    
    table = Table(show_header=True, header_style="bold green")
    table.add_column("Command", style="cyan", width=30)
    table.add_column("Explanation", style="white", max_width=50)
    
    for suggestion in suggestions[:limit]:
        # Get explanation for the suggestion
        if suggestion in command_filter.direct_commands:
            explanation = command_filter.direct_commands[suggestion]['explanation']
        elif suggestion in command_filter.direct_commands_with_args:
            explanation = command_filter.direct_commands_with_args[suggestion]['explanation']
        else:
            explanation = "No explanation available"
        
        # Truncate long explanations
        if len(explanation) > 47:
            explanation = explanation[:44] + "..."
        
        table.add_row(suggestion, explanation)
    
    console.print(table)

@filter.command()
@click.argument('natural_language')
@click.argument('command')
@click.argument('explanation')
@click.option('--confidence', '-c', default=0.95, help='Confidence score (0.0-1.0)')
@click.pass_context
def add(ctx, natural_language, command, explanation, confidence):
    """Add a custom direct command mapping"""
    
    if not (0.0 <= confidence <= 1.0):
        console.print("[red]Confidence must be between 0.0 and 1.0[/red]")
        return
    
    ai_translator = ctx.obj['ai_translator']
    command_filter = ai_translator.command_filter
    
    # Check if command already exists
    if command_filter.is_direct_command(natural_language):
        from rich.prompt import Confirm
        if not Confirm.ask(f"Command '{natural_language}' already exists. Overwrite?", default=False):
            console.print("[yellow]Operation cancelled.[/yellow]")
            return
    
    # Add the custom command
    command_filter.add_custom_command(natural_language, command, explanation, confidence)
    
    console.print(f"[green]✓ Added custom command:[/green]")
    console.print(f"  Natural Language: [cyan]{natural_language}[/cyan]")
    console.print(f"  Command: [white]{command}[/white]")
    console.print(f"  Explanation: {explanation}")
    console.print(f"  Confidence: {confidence:.0%}")

@filter.command()
@click.argument('natural_language')
@click.pass_context
def remove(ctx, natural_language):
    """Remove a custom direct command"""
    
    ai_translator = ctx.obj['ai_translator']
    command_filter = ai_translator.command_filter
    
    # Check if it's a custom command
    custom_commands = command_filter.list_custom_commands()
    if natural_language.lower() not in custom_commands:
        console.print(f"[red]'{natural_language}' is not a custom command or doesn't exist.[/red]")
        return
    
    # Remove the command
    removed = command_filter.remove_custom_command(natural_language)
    
    if removed:
        console.print(f"[green]✓ Removed custom command: '{natural_language}'[/green]")
    else:
        console.print(f"[red]Failed to remove command: '{natural_language}'[/red]")

@filter.command()
@click.pass_context
def custom(ctx):
    """List all custom commands"""
    
    ai_translator = ctx.obj['ai_translator']
    command_filter = ai_translator.command_filter
    
    custom_commands = command_filter.list_custom_commands()
    
    if not custom_commands:
        console.print("[yellow]No custom commands defined.[/yellow]")
        return
    
    table = Table(show_header=True, header_style="bold magenta", title="Custom Commands")
    table.add_column("Natural Language", style="cyan", max_width=25)
    table.add_column("Command", style="white", max_width=30)
    table.add_column("Explanation", style="white", max_width=40)
    table.add_column("Confidence", style="green", width=10)
    
    for nl, details in custom_commands.items():
        confidence = f"{details['confidence']:.0%}"
        
        # Truncate long text
        command = details['command']
        if len(command) > 27:
            command = command[:24] + "..."
        
        explanation = details['explanation']
        if len(explanation) > 37:
            explanation = explanation[:34] + "..."
        
        table.add_row(nl, command, explanation, confidence)
    
    console.print(table)

@filter.command()
@click.argument('test_input')
@click.pass_context
def test(ctx, test_input):
    """Test if input would be recognized as a direct command"""
    
    ai_translator = ctx.obj['ai_translator']
    command_filter = ai_translator.command_filter
    
    is_direct = command_filter.is_direct_command(test_input)
    
    if is_direct:
        result = command_filter.get_direct_command_result(test_input)
        
        console.print(f"[green]✓ '{test_input}' is recognized as a direct command[/green]")
        
        # Show details
        details_table = Table(show_header=True, header_style="bold green")
        details_table.add_column("Property", style="cyan", width=15)
        details_table.add_column("Value", style="white")
        
        details_table.add_row("Command", result['command'])
        details_table.add_row("Explanation", result['explanation'])
        details_table.add_row("Confidence", f"{result['confidence']:.0%}")
        details_table.add_row("Source", result['source'])
        details_table.add_row("Type", "Custom" if result.get('custom') else "Built-in")
        
        console.print(details_table)
        
    else:
        console.print(f"[red]✗ '{test_input}' is not recognized as a direct command[/red]")
        
        # Show suggestions
        suggestions = command_filter.get_command_suggestions(test_input)
        if suggestions:
            console.print(f"\n[dim]Did you mean one of these?[/dim]")
            for i, suggestion in enumerate(suggestions[:5], 1):
                console.print(f"  {i}. [cyan]{suggestion}[/cyan]")

@filter.command()
@click.pass_context  
def benchmark(ctx):
    """Benchmark direct command performance"""
    
    import time
    
    ai_translator = ctx.obj['ai_translator']
    command_filter = ai_translator.command_filter
    
    test_commands = [
        "ls", "git status", "ps aux", "ls -la", "docker ps",
        "python --version", "npm list", "df -h", "free -h", "uptime"
    ]
    
    console.print("[bold]Benchmarking Direct Command Performance[/bold]")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Command", style="cyan", width=20)
    table.add_column("Time (ms)", style="green", width=12)
    table.add_column("Recognized", style="white", width=12)
    table.add_column("Confidence", style="white", width=12)
    
    total_time = 0
    recognized_count = 0
    
    for cmd in test_commands:
        # Measure detection time
        start_time = time.perf_counter()
        is_direct = command_filter.is_direct_command(cmd)
        detection_time = time.perf_counter() - start_time
        
        # Measure result retrieval time if recognized
        if is_direct:
            start_time = time.perf_counter()
            result = command_filter.get_direct_command_result(cmd)
            result_time = time.perf_counter() - start_time
            total_cmd_time = detection_time + result_time
            confidence = f"{result['confidence']:.0%}"
            recognized_count += 1
        else:
            total_cmd_time = detection_time
            confidence = "N/A"
        
        total_time += total_cmd_time
        
        table.add_row(
            cmd,
            f"{total_cmd_time * 1000:.3f}",
            "✓" if is_direct else "✗",
            confidence
        )
    
    console.print(table)
    
    # Summary statistics
    avg_time = total_time / len(test_commands)
    recognition_rate = (recognized_count / len(test_commands)) * 100
    
    summary_table = Table(show_header=True, header_style="bold blue", title="Benchmark Summary")
    summary_table.add_column("Metric", style="cyan", width=20)
    summary_table.add_column("Value", style="white")
    
    summary_table.add_row("Total Commands", str(len(test_commands)))
    summary_table.add_row("Recognized", str(recognized_count))
    summary_table.add_row("Recognition Rate", f"{recognition_rate:.1f}%")
    summary_table.add_row("Average Time", f"{avg_time * 1000:.3f} ms")
    summary_table.add_row("Total Time", f"{total_time * 1000:.3f} ms")
    
    console.print(summary_table)