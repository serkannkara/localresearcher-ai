"""Workflow orchestrator for agent execution."""

from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from localresearcher.core.schemas import (
    Task,
    WorkflowState,
    AgentStep,
    AgentOutput,
    Report,
)
from localresearcher.core.intent import IntentType
from localresearcher.llm.ollama import OllamaProvider
from localresearcher.rag.vector_store import VectorStore
from localresearcher.rag.loader import load_document
from localresearcher.agents.intent_classifier import IntentClassifier
from localresearcher.agents.planner import PlannerAgent
from localresearcher.agents.researcher import ResearcherAgent
from localresearcher.agents.analyst import AnalystAgent
from localresearcher.agents.critic import CriticAgent
from localresearcher.agents.writer import WriterAgent


class ResearchWorkflow:
    """Orchestrates the multi-agent research workflow."""
    
    def __init__(self):
        self.console = Console()
        self.llm = OllamaProvider()
        self.vector_store = VectorStore()
        
        # Initialize agents
        self.intent_classifier = IntentClassifier(self.llm)
        self.planner = PlannerAgent(self.llm)
        self.researcher = ResearcherAgent(self.llm, self.vector_store)
        self.analyst = AnalystAgent(self.llm)
        self.critic = CriticAgent(self.llm)
        self.writer = WriterAgent(self.llm)
    
    async def check_ollama(self) -> bool:
        """Check if Ollama is available."""
        is_available = await self.llm.is_available()
        if not is_available:
            self.console.print(
                Panel(
                    "[red]Ollama is not available or model is not installed.[/red]\n\n"
                    f"Please ensure Ollama is running and the model '{self.llm.model}' is installed:\n"
                    f"  ollama pull {self.llm.model}",
                    title="❌ Connection Error",
                    border_style="red",
                )
            )
        return is_available
    
    async def load_documents(self, file_paths: list[Path]) -> Task:
        """Load documents and create a task."""
        documents = []
        
        for path in file_paths:
            if not path.exists():
                self.console.print(f"[yellow]Warning: File not found: {path}[/yellow]")
                continue
            
            try:
                doc = load_document(path)
                documents.append(doc)
                await self.vector_store.add_document(doc)
            except Exception as e:
                self.console.print(f"[yellow]Warning: Failed to load {path}: {e}[/yellow]")
        
        return Task(query="", documents=documents)
    
    async def execute(self, query: str, file_paths: list[Path] | None = None) -> Report:
        """Execute the full research workflow."""
        # Check Ollama availability
        if not await self.check_ollama():
            raise RuntimeError("Ollama is not available")
        
        # CRITICAL: Validate files FIRST, before any processing
        has_documents = bool(file_paths)
        task = Task(query=query)
        
        if file_paths:
            # Validate ALL files exist before proceeding
            missing_files = [f for f in file_paths if not f.exists()]
            
            if missing_files:
                # Fail fast with clear error - DO NOT continue
                error_msg = "❌ File(s) not found:\n" + "\n".join(
                    f"  • {f}" for f in missing_files
                )
                self.console.print(
                    Panel(
                        f"[red]{error_msg}[/red]\n\n"
                        "[yellow]Please check:[/yellow]\n"
                        "  • File path is correct\n"
                        "  • File exists in the specified location\n"
                        "  • You have read permissions\n\n"
                        "[dim]Example:[/dim]\n"
                        "  [cyan]localresearcher ask \"Analyze\" --files ./examples/sample.md[/cyan]",
                        title="❌ File Not Found",
                        border_style="red",
                    )
                )
                raise FileNotFoundError(f"Missing files: {', '.join(str(f) for f in missing_files)}")
            
            # Files exist - load them
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                progress.add_task("📄 Loading documents...", total=None)
                task = await self.load_documents(file_paths)
                task.query = query
        
        # NOW do intent detection (after file validation)
        self.console.print("[cyan]🧠 Detecting intent...[/cyan]")
        intent_result = await self.intent_classifier.classify(query, has_documents)
        
        # Handle non-research intents
        if intent_result.intent.type in [IntentType.GREETING, IntentType.SMALL_TALK]:
            self.console.print(
                f"[dim]Intent: {intent_result.intent.type.value} "
                f"(confidence: {intent_result.intent.confidence:.0%})[/dim]\n"
            )
            
            # Return simple response without research pipeline
            report = Report(
                task_id=task.id,
                title=query[:100],
                content=intent_result.suggested_response or "Hello!",
                metadata={
                    "intent": intent_result.intent.type.value,
                    "confidence": intent_result.intent.confidence,
                    "research_performed": False,
                    "document_count": 0,
                },
            )
            
            return report
        
        # Research intent detected - proceed with pipeline
        self.console.print(
            f"[green]✓ Research intent detected[/green] "
            f"[dim](confidence: {intent_result.intent.confidence:.0%})[/dim]\n"
        )
        
        # Show evidence status
        if not has_documents:
            self.console.print(
                Panel(
                    "[bold yellow]⚠️  Internal Knowledge Mode Only[/bold yellow]\n\n"
                    "[bold]Quick Summary:[/bold]\n"
                    "  • No documents provided\n"
                    "  • No web search available\n"
                    "  • No external evidence\n"
                    "  • Response from model's training data\n\n"
                    "[bold]Sources:[/bold]\n"
                    "  ✓ Local language model knowledge\n\n"
                    "[bold]Documents:[/bold]\n"
                    "  ❌ None provided\n\n"
                    "[bold]Web Search:[/bold]\n"
                    "  ❌ Not available (feature coming in v0.3.0)\n\n"
                    "[bold]Evidence Status:[/bold]\n"
                    "  ❌ No citations available\n\n"
                    "[bold]Expected Confidence:[/bold]\n"
                    "  🟢 With documents: HIGH\n"
                    "  🟡 With web search: MEDIUM-HIGH\n"
                    "  🔴 Current mode: LOW\n\n"
                    "[dim]This is an AI-generated explanation, not verified research.\n"
                    "For verifiable results, provide documents or enable web search.[/dim]\n\n"
                    "[bold]For evidence-backed research:[/bold]\n"
                    "  [cyan]localresearcher ask \"your query\" --files document.pdf[/cyan]",
                    title="🧠 Knowledge Mode",
                    border_style="yellow",
                )
            )
        else:
            self.console.print(
                Panel(
                    f"[bold green]✓ Evidence-Based Research Mode[/bold green]\n\n"
                    f"[bold]Quick Summary:[/bold]\n"
                    f"  • {len(task.documents)} document(s) loaded\n"
                    f"  • Evidence-backed analysis\n"
                    f"  • Citations will be provided\n"
                    f"  • Higher confidence ratings\n\n"
                    f"[bold]Sources:[/bold]\n"
                    f"  ✓ Local language model knowledge\n"
                    f"  ✓ {len(task.documents)} document(s) analyzed\n\n"
                    f"[bold]Documents:[/bold]\n" +
                    "\n".join(f"  • {doc.metadata.get('source', 'Unknown')}" 
                             for doc in task.documents[:5]) +
                    (f"\n  [dim]... and {len(task.documents) - 5} more[/dim]" 
                     if len(task.documents) > 5 else "") +
                    "\n\n[bold]Web Search:[/bold]\n"
                    "  ❌ Not available (feature coming in v0.3.0)\n\n"
                    "[bold]Evidence Status:[/bold]\n"
                    "  ✅ Citations will be provided\n\n"
                    "[bold]Expected Confidence:[/bold]\n"
                    "  🟢 Current mode: MEDIUM-HIGH\n"
                    "  🟡 With web search added: HIGH\n"
                    "  🔴 Without documents: LOW\n\n"
                    "[dim]This analysis is based on the provided documents.\n"
                    "All claims will be backed by source citations.[/dim]",
                    title="🔬 Evidence Mode",
                    border_style="green",
                )
            )
        
        # Initialize workflow state
        state = WorkflowState(task=task)
        
        # Execute workflow steps with context-aware messages
        total_steps = 5
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            # Step 1: Planning
            if has_documents:
                step_1_msg = f"[cyan][1/{total_steps}] 📋 Planning research approach..."
            else:
                step_1_msg = f"[cyan][1/{total_steps}] 🧠 Organizing internal knowledge..."
            
            task_progress = progress.add_task(step_1_msg, total=None)
            state.current_step = AgentStep.PLANNING
            state.plan = await self.planner.plan(task)
            state.outputs.append(
                AgentOutput(step=AgentStep.PLANNING, content=state.plan)
            )
            progress.update(task_progress, completed=True)
            
            # Step 2: Researching (context-aware message)
            if has_documents:
                step_message = f"[cyan][2/{total_steps}] 🔍 Retrieving evidence from documents..."
            else:
                step_message = f"[cyan][2/{total_steps}] 🧠 Building response from model knowledge..."
            
            progress.update(task_progress, description=step_message)
            state.current_step = AgentStep.RESEARCHING
            state.research_findings = await self.researcher.research(query, state.plan)
            state.outputs.append(
                AgentOutput(step=AgentStep.RESEARCHING, content=state.research_findings)
            )
            
            # Step 3: Analyzing
            if has_documents:
                step_3_msg = f"[cyan][3/{total_steps}] 📊 Analyzing evidence..."
            else:
                step_3_msg = f"[cyan][3/{total_steps}] 📊 Structuring explanation..."
            
            progress.update(task_progress, description=step_3_msg)
            state.current_step = AgentStep.ANALYZING
            state.analysis = await self.analyst.analyze(
                query, state.plan, state.research_findings
            )
            state.outputs.append(
                AgentOutput(step=AgentStep.ANALYZING, content=state.analysis)
            )
            
            # Step 4: Critiquing
            progress.update(
                task_progress, 
                description=f"[cyan][4/{total_steps}] 🔎 Evaluating completeness..."
            )
            state.current_step = AgentStep.CRITIQUING
            state.critique = await self.critic.critique(query, state.analysis)
            state.outputs.append(
                AgentOutput(step=AgentStep.CRITIQUING, content=state.critique)
            )
            
            # Step 5: Writing
            if has_documents:
                step_5_msg = f"[cyan][5/{total_steps}] ✍️  Writing research report..."
            else:
                step_5_msg = f"[cyan][5/{total_steps}] ✍️  Formatting response..."
            
            progress.update(task_progress, description=step_5_msg)
            state.current_step = AgentStep.WRITING
            
            # Generate report with evidence flag
            state.final_report = await self.writer.write_report(
                query,
                state.plan,
                state.research_findings,
                state.analysis,
                state.critique,
                has_external_sources=has_documents,
            )
            
            # Add knowledge mode notices (top AND bottom) if no documents
            if not has_documents:
                top_notice = """# 🧠 Knowledge Mode Report

⚠️  **Important Notice**

This response is generated from the language model's internal knowledge only.

**No external sources were used:**
- ❌ No documents analyzed
- ❌ No web searches performed
- ❌ No citations available
- ❌ No interviews or empirical data

**Information Status:**
- May be outdated (model training cutoff)
- Cannot be verified against sources
- Represents general knowledge, not specific research

**For evidence-backed research with citations:**"""
                state.final_report = top_notice + "\n\n" + state.final_report
            
            state.outputs.append(
                AgentOutput(step=AgentStep.WRITING, content=state.final_report)
            )
        
        # Create report
        report = Report(
            task_id=task.id,
            title=query[:100],
            content=state.final_report,
            metadata={
                "intent": intent_result.intent.type.value,
                "confidence": intent_result.intent.confidence,
                "research_performed": True,
                "steps": len(state.outputs),
                "document_count": len(task.documents),
                "has_external_evidence": has_documents,
            },
        )
        
        return report
    
    async def cleanup(self) -> None:
        """Cleanup resources."""
        await self.llm.close()
        await self.vector_store.close()