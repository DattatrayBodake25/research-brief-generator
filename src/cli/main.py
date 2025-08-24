import typer
import asyncio
import json
from typing import Optional
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.markdown import Markdown
from src.core.graph import research_graph
from src.models.schemas import BriefRequest
from src.utils.logger import logger
import uuid

console = Console()
app = typer.Typer(help="Research Brief Generator CLI")

@app.command()
def generate_brief(
    topic: str = typer.Argument(..., help="Research topic"),
    depth: int = typer.Option(3, "--depth", "-d", help="Research depth (1-5)"),
    follow_up: bool = typer.Option(False, "--follow-up", "-f", help="Follow-up query"),
    user_id: str = typer.Option("default-user", "--user", "-u", help="User ID"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    show_full: bool = typer.Option(False, "--full", "-F", help="Show full brief content")
):
    """Generate a research brief from command line"""
    try:
        # Create request
        request = BriefRequest(
            topic=topic,
            depth=depth,
            follow_up=follow_up,
            user_id=user_id
        )
        
        # Execute with progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating research brief...", total=None)
            
            # Run async workflow
            async def run_workflow():
                state = {
                    "topic": request.topic,
                    "depth": request.depth,
                    "user_id": request.user_id,
                    "follow_up": request.follow_up
                }
                
                result = await research_graph.ainvoke(state)
                return result
            
            final_state = asyncio.run(run_workflow())
            progress.update(task, completed=True)
        
        # Handle results
        if final_state.get("final_brief"):
            brief = final_state["final_brief"]
            
            console.print("\n[green]✓ Research brief generated successfully![/green]")
            console.print(f"\n[b]Topic:[/b] {brief.topic}")
            console.print(f"[b]Brief ID:[/b] {brief.brief_id}")
            console.print(f"[b]Generated:[/b] {brief.generated_at}")
            
            # Display brief content based on user preference
            if show_full:
                display_full_brief(brief)
            else:
                display_brief_summary(brief)
            
            # Auto-generate filename if not provided
            if not output:
                # Create auto filename based on topic and timestamp
                safe_topic = "".join(c if c.isalnum() else "_" for c in topic.lower())
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output = Path(f"research_brief_{safe_topic}_{timestamp}.json")
            
            # Save to file
            output.write_text(brief.model_dump_json(indent=2))
            console.print(f"[green]✓ Brief saved to: {output}[/green]")
            
            return brief.model_dump()
            
        else:
            console.print("[red]✗ Failed to generate brief[/red]")
            if final_state.get("errors"):
                for error in final_state["errors"]:
                    console.print(f"[red]Error: {error}[/red]")
            return None
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

def display_brief_summary(brief):
    """Display a summary of the research brief"""
    console.print(Panel.fit(
        f"[bold]Executive Summary:[/bold]\n{brief.executive_summary}",
        title="📋 Brief Summary",
        border_style="blue"
    ))
    
    console.print(f"\n[bold]Key Findings:[/bold] ({len(brief.key_findings)})")
    for i, finding in enumerate(brief.key_findings[:3], 1):  # Show first 3
        console.print(f"  {i}. {finding}")
    if len(brief.key_findings) > 3:
        console.print(f"  ... and {len(brief.key_findings) - 3} more findings")
    
    if brief.recommendations:
        console.print(f"\n[bold]Recommendations:[/bold] ({len(brief.recommendations)})")
        for i, rec in enumerate(brief.recommendations[:2], 1):  # Show first 2
            console.print(f"  {i}. {rec}")
        if len(brief.recommendations) > 2:
            console.print(f"  ... and {len(brief.recommendations) - 2} more recommendations")
    
    console.print(f"\n[bold]References:[/bold] ({len(brief.references)})")
    for ref in brief.references[:2]:  # Show first 2 references
        console.print(f"  • {ref.title}")
    
    console.print(f"\n[i]Use --full to see complete brief or check the saved JSON file[/i]")

def display_full_brief(brief):
    """Display the complete research brief"""
    console.print(Panel.fit(
        f"[bold]Executive Summary[/bold]\n\n{brief.executive_summary}",
        title="📋 Executive Summary",
        border_style="green"
    ))
    
    console.print(Panel.fit(
        "\n".join([f"• {finding}" for finding in brief.key_findings]),
        title="🔍 Key Findings",
        border_style="yellow"
    ))
    
    console.print(Panel.fit(
        brief.detailed_analysis,
        title="📊 Detailed Analysis", 
        border_style="blue"
    ))
    
    if brief.recommendations:
        console.print(Panel.fit(
            "\n".join([f"• {rec}" for rec in brief.recommendations]),
            title="💡 Recommendations",
            border_style="magenta"
        ))
    
    console.print(Panel.fit(
        "\n".join([f"• {ref.title} - {ref.url}" for ref in brief.references]),
        title="📚 References",
        border_style="cyan"
    ))
    
    console.print(f"\n[dim]Brief ID: {brief.brief_id}[/dim]")
    console.print(f"[dim]Generated: {brief.generated_at}[/dim]")

@app.command()
def list_tools():
    """List available search tools"""
    from src.core.tools import search_tools
    tools = search_tools.get_available_tools()
    
    console.print("\n[bold]Available Search Tools:[/bold]")
    for tool in tools:
        console.print(f"• {tool.name}: {tool.description}")

@app.command()
def view_brief(file_path: Path = typer.Argument(..., help="Path to brief JSON file")):
    """View a previously generated research brief"""
    try:
        if not file_path.exists():
            console.print(f"[red]File not found: {file_path}[/red]")
            return
        
        content = file_path.read_text()
        brief_data = json.loads(content)
        
        # Convert back to Pydantic model for proper display
        from src.models.schemas import FinalBrief
        brief = FinalBrief(**brief_data)
        
        console.print(f"\n[green]Loaded brief from: {file_path}[/green]")
        display_full_brief(brief)
        
    except Exception as e:
        console.print(f"[red]Error loading brief: {e}[/red]")

if __name__ == "__main__":
    app()