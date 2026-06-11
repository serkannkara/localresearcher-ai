"""CLI interface for LocalResearcherAI."""

import asyncio
from pathlib import Path
from typing import Annotated
import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from localresearcher.core.config import settings
from localresearcher.core.workflow import ResearchWorkflow
from localresearcher.core.intent import IntentType

app = typer.Typer(
    name="localresearcher",
    help="Local-first agentic research system using local LLMs",
    add_completion=False,
)

console = Console()


@app.command()
def ask(
    query: Annotated[str, typer.Argument(help="Research question or task")],
    files: Annotated[
        list[Path] | None,
        typer.Option("--files", "-f", help="Files to analyze"),
    ] = None,
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output file path"),
    ] = None,
) -> None:
    """
    Ask a research question and get a comprehensive report.
    
    Examples:
        localresearcher ask "Analyze Apple's AI strategy"
        localresearcher ask "Summarize key findings" --files report.pdf
        localresearcher ask "Create action plan" --files ./docs/*.md
    """
    asyncio.run(_ask_async(query, files, output))


async def _ask_async(
    query: str,
    files: list[Path] | None,
    output: Path | None,
) -> None:
    """Async implementation of ask command."""
    console.print(
        Panel(
            f"[bold cyan]Query:[/bold cyan] {query}\n\n"
            f"[bold cyan]Model:[/bold cyan] {settings.ollama_model}\n"
            f"[bold cyan]Files:[/bold cyan] {len(files) if files else 0}",
            title="🔬 LocalResearcherAI",
            border_style="cyan",
        )
    )
    
    workflow = ResearchWorkflow()
    
    try:
        # Execute workflow
        report = await workflow.execute(query, files)
        
        # Get intent type from metadata
        intent_type = report.metadata.get("intent", "unknown")
        research_performed = report.metadata.get("research_performed", False)
        
        # Determine panel title and style based on intent
        if intent_type == IntentType.GREETING.value:
            panel_title = "👋 Greeting"
            panel_style = "green"
        elif intent_type == IntentType.SMALL_TALK.value:
            panel_title = "💬 Conversation"
            panel_style = "blue"
        elif research_performed:
            # Check if it's knowledge mode or evidence mode
            has_evidence = report.metadata.get("has_external_evidence", False)
            if has_evidence:
                panel_title = "🔬 Evidence-Based Research Report"
                panel_style = "green"
            else:
                panel_title = "🧠 Knowledge Report"
                panel_style = "yellow"
        else:
            panel_title = "💡 Response"
            panel_style = "cyan"
        
        # Display report
        console.print("\n")
        console.print(
            Panel(
                Markdown(report.content),
                title=panel_title,
                border_style=panel_style,
            )
        )
        
        # Only save to file for research reports
        should_save = research_performed and intent_type == IntentType.RESEARCH.value
        
        if should_save:
            # Save to file
            if output is None:
                output = settings.reports_path / f"report_{report.id}.md"
            
            output.parent.mkdir(exist_ok=True, parents=True)
            output.write_text(report.content, encoding="utf-8")
            
            console.print(f"\n[green]✓ Report saved to:[/green] {output}")
        else:
            # For greetings/small talk, just show in terminal
            console.print(
                f"\n[dim]💡 Tip: For research reports that can be saved, "
                f"try queries like:[/dim]"
            )
            console.print(
                f"[dim]   localresearcher ask \"Analyze topic\" --files doc.pdf[/dim]"
            )
        
    except FileNotFoundError as e:
        # File not found - already displayed nice error in workflow
        console.print(f"\n[red]✗ Cannot proceed without valid files.[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]✗ Error:[/red] {e}")
        raise typer.Exit(1)
    finally:
        await workflow.cleanup()


@app.command()
def version() -> None:
    """Show version information."""
    from localresearcher import __version__
    
    console.print(
        Panel(
            f"[bold]LocalResearcherAI[/bold]\n"
            f"Version: {__version__}\n"
            f"Model: {settings.ollama_model}\n"
            f"Ollama URL: {settings.ollama_base_url}",
            title="ℹ️  Version Info",
            border_style="blue",
        )
    )


if __name__ == "__main__":
    app()