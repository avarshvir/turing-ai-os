import sys
import os
import subprocess
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from skills.shell_ops import ShellAgent

console = Console()

def clear_screen():
    os.system('clear')

def main_loop():
    clear_screen()
    print("\033]0;Turing AI Terminal\007", end="")
    agent = ShellAgent()
    
    # Welcome Banner
    welcome_text = Text("Turing AI Shell [Version 1.0]\n", style="bold cyan")
    welcome_text.append("Natural Language Terminal interface. Type 'exit' to return to legacy bash.", style="dim")
    console.print(Panel(welcome_text, title="System Core", expand=False, border_style="cyan"))

    while True:
        try:
            # The custom prompt
            user_input = Prompt.ask("\n[bold green]turing@os[/bold green]:[bold blue]~[/bold blue]$ ")
            
            if not user_input.strip():
                continue
                
            if user_input.lower() in ['exit', 'quit']:
                console.print("[dim]Returning to legacy terminal...[/dim]")
                break
            if user_input.lower() == 'clear':
                clear_screen()
                continue

            # 1. Show thinking state
            with console.status("[bold cyan]Translating intent to system command...", spinner="dots"):
                bash_command = agent.translate_to_bash(user_input)
            
            # 2. Safety Check (Explain-before-execute)
            console.print(f"\n[bold yellow]Proposed Command:[/bold yellow] [bold white on black] {bash_command} [/bold white on black]")
            
            confirm = Prompt.ask("[bold red]Execute this command?[/bold red] (y/n)", choices=["y", "n"], default="n")
            
            # 3. Execution
            if confirm == 'y':
                console.print(f"[dim]Executing: {bash_command}[/dim]\n")
                
                # Run command directly in the OS and stream output
                process = subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                # Read output line by line so it feels like a real terminal
                for line in process.stdout:
                    console.print(line, end="")
                for err_line in process.stderr:
                    console.print(f"[bold red]{err_line}[/bold red]", end="")
                    
                process.wait()
            else:
                console.print("[yellow]Action Cancelled.[/yellow]")

        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            console.print("\n[yellow]Process interrupted. Type 'exit' to close.[/yellow]")
        except Exception as e:
            console.print(f"\n[bold red]System Error:[/bold red] {str(e)}")

if __name__ == "__main__":
    main_loop()
