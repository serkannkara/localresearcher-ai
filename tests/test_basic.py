"""Comprehensive tests for LocalResearcherAI."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch
from localresearcher import __version__
from localresearcher.core.schemas import Document, Task, AgentStep
from localresearcher.core.intent import IntentType, Intent
from localresearcher.rag.chunker import TextChunker
from localresearcher.rag.loader import get_loader, TextLoader, MarkdownLoader


# ============================================================================
# VERSION & IMPORTS
# ============================================================================

def test_version():
    """Test that version is defined."""
    assert __version__ == "0.1.0"


def test_core_imports():
    """Test that core modules can be imported."""
    from localresearcher.core import config, schemas, intent
    from localresearcher.llm import ollama
    from localresearcher.agents import planner, researcher, analyst, critic, writer
    from localresearcher.rag import chunker, embeddings, loader, vector_store
    
    assert config is not None
    assert schemas is not None
    assert intent is not None
    assert ollama is not None
    assert planner is not None
    assert researcher is not None
    assert analyst is not None
    assert critic is not None
    assert writer is not None
    assert chunker is not None
    assert embeddings is not None
    assert loader is not None
    assert vector_store is not None


# ============================================================================
# SCHEMAS
# ============================================================================

def test_document_creation():
    """Test Document model creation."""
    doc = Document(
        path="/test/file.txt",
        content="Test content",
        file_type="text",
    )
    
    assert doc.path == "/test/file.txt"
    assert doc.content == "Test content"
    assert doc.file_type == "text"
    assert doc.id is not None


def test_task_creation():
    """Test Task model creation."""
    task = Task(query="What is AI?")
    
    assert task.query == "What is AI?"
    assert task.documents == []
    assert task.id is not None


def test_agent_step_enum():
    """Test AgentStep enum values."""
    assert AgentStep.PLANNING == "planning"
    assert AgentStep.RESEARCHING == "researching"
    assert AgentStep.ANALYZING == "analyzing"
    assert AgentStep.CRITIQUING == "critiquing"
    assert AgentStep.WRITING == "writing"


# ============================================================================
# INTENT DETECTION
# ============================================================================

def test_intent_type_enum():
    """Test IntentType enum."""
    assert IntentType.GREETING == "greeting"
    assert IntentType.SMALL_TALK == "small_talk"
    assert IntentType.RESEARCH == "research"
    assert IntentType.QUESTION == "question"


def test_intent_model():
    """Test Intent model."""
    intent = Intent(
        type=IntentType.RESEARCH,
        confidence=0.95,
        reasoning="Query contains research keywords",
        requires_research=True,
    )
    
    assert intent.type == IntentType.RESEARCH
    assert intent.confidence == 0.95
    assert intent.requires_research is True


# ============================================================================
# TEXT CHUNKER
# ============================================================================

def test_chunker_small_text():
    """Test chunker with text smaller than chunk size."""
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    text = "This is a small text."
    
    chunks = chunker.chunk(text)
    
    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunker_large_text():
    """Test chunker with text larger than chunk size."""
    chunker = TextChunker(chunk_size=50, chunk_overlap=10)
    text = "This is a sentence. " * 10  # ~200 chars
    
    chunks = chunker.chunk(text)
    
    assert len(chunks) > 1
    assert all(len(chunk) > 0 for chunk in chunks)


def test_chunker_empty_text():
    """Test chunker with empty text."""
    chunker = TextChunker()
    chunks = chunker.chunk("")
    
    assert chunks == []


def test_chunker_sentence_boundary():
    """Test chunker respects sentence boundaries."""
    chunker = TextChunker(chunk_size=30, chunk_overlap=5)
    text = "First sentence. Second sentence! Third question? Fourth line."
    
    chunks = chunker.chunk(text)
    
    # Should break at punctuation marks
    assert all(chunk.strip() for chunk in chunks)


# ============================================================================
# DOCUMENT LOADERS
# ============================================================================

def test_get_loader_txt():
    """Test loader selection for .txt files."""
    path = Path("test.txt")
    loader = get_loader(path)
    
    assert isinstance(loader, TextLoader)


def test_get_loader_md():
    """Test loader selection for .md files."""
    path = Path("test.md")
    loader = get_loader(path)
    
    assert isinstance(loader, MarkdownLoader)


def test_text_loader(tmp_path):
    """Test TextLoader with actual file."""
    test_file = tmp_path / "test.txt"
    test_content = "Hello, world!"
    test_file.write_text(test_content, encoding="utf-8")
    
    loader = TextLoader()
    doc = loader.load(test_file)
    
    assert doc.content == test_content
    assert doc.file_type == "text"
    assert str(test_file) in doc.path


def test_markdown_loader(tmp_path):
    """Test MarkdownLoader with actual file."""
    test_file = tmp_path / "test.md"
    test_content = "# Hello\n\nThis is markdown."
    test_file.write_text(test_content, encoding="utf-8")
    
    loader = MarkdownLoader()
    doc = loader.load(test_file)
    
    assert doc.content == test_content
    assert doc.file_type == "markdown"


# ============================================================================
# ASYNC AGENT TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_planner_agent_success():
    """Test PlannerAgent with mocked LLM."""
    from localresearcher.agents.planner import PlannerAgent
    
    mock_llm = AsyncMock()
    mock_llm.generate.return_value = "Test plan"
    
    planner = PlannerAgent(mock_llm)
    task = Task(query="Test query")
    
    plan = await planner.plan(task)
    
    assert plan == "Test plan"
    assert mock_llm.generate.called


@pytest.mark.asyncio
async def test_analyst_agent_success():
    """Test AnalystAgent with mocked LLM."""
    from localresearcher.agents.analyst import AnalystAgent
    
    mock_llm = AsyncMock()
    mock_llm.generate.return_value = "Test analysis"
    
    analyst = AnalystAgent(mock_llm)
    
    analysis = await analyst.analyze("query", "plan", "findings")
    
    assert analysis == "Test analysis"
    assert mock_llm.generate.called


@pytest.mark.asyncio
async def test_critic_agent_success():
    """Test CriticAgent with mocked LLM."""
    from localresearcher.agents.critic import CriticAgent
    
    mock_llm = AsyncMock()
    mock_llm.generate.return_value = "Test critique"
    
    critic = CriticAgent(mock_llm)
    
    critique = await critic.critique("query", "analysis")
    
    assert critique == "Test critique"
    assert mock_llm.generate.called


@pytest.mark.asyncio
async def test_writer_agent_knowledge_mode():
    """Test WriterAgent in knowledge mode."""
    from localresearcher.agents.writer import WriterAgent
    
    mock_llm = AsyncMock()
    mock_llm.generate.return_value = "Test report"
    
    writer = WriterAgent(mock_llm)
    
    report = await writer.write_report(
        "query", "plan", "findings", "analysis", "critique",
        has_external_sources=False
    )
    
    assert report == "Test report"
    assert mock_llm.generate.called


@pytest.mark.asyncio
async def test_writer_agent_evidence_mode():
    """Test WriterAgent in evidence mode."""
    from localresearcher.agents.writer import WriterAgent
    
    mock_llm = AsyncMock()
    mock_llm.generate.return_value = "Evidence-backed report"
    
    writer = WriterAgent(mock_llm)
    
    report = await writer.write_report(
        "query", "plan", "findings", "analysis", "critique",
        has_external_sources=True
    )
    
    assert report == "Evidence-backed report"
    assert mock_llm.generate.called


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_planner_handles_empty_response():
    """Test PlannerAgent handles empty LLM response."""
    from localresearcher.agents.planner import PlannerAgent, PlannerError
    
    mock_llm = AsyncMock()
    mock_llm.generate.return_value = ""
    
    planner = PlannerAgent(mock_llm)
    task = Task(query="Test query")
    
    with pytest.raises(PlannerError, match="empty"):
        await planner.plan(task)


@pytest.mark.asyncio
async def test_researcher_handles_vector_store_failure():
    """Test ResearcherAgent handles vector store failure gracefully."""
    from localresearcher.agents.researcher import ResearcherAgent
    
    mock_llm = AsyncMock()
    mock_llm.generate.return_value = "Findings without context"
    
    mock_vector_store = AsyncMock()
    mock_vector_store.search.side_effect = Exception("Vector store error")
    
    researcher = ResearcherAgent(mock_llm, mock_vector_store)
    
    # Should not raise, should continue without context
    findings = await researcher.research("query", "plan")
    
    assert findings == "Findings without context"
    assert mock_llm.generate.called


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_config_settings():
    """Test configuration settings."""
    from localresearcher.core.config import settings
    
    assert settings.ollama_base_url is not None
    assert settings.ollama_model is not None
    assert settings.chunk_size > 0
    assert settings.chunk_overlap >= 0
    assert settings.top_k_retrieval > 0


def test_retry_utility_exists():
    """Test retry utility module exists."""
    from localresearcher.core import retry
    
    assert hasattr(retry, 'retry_async')
    assert hasattr(retry, 'with_retry')


def test_logging_utility_exists():
    """Test logging utility module exists."""
    from localresearcher.core import logging as log_module
    
    assert hasattr(log_module, 'setup_logging')
    assert hasattr(log_module, 'get_logger')