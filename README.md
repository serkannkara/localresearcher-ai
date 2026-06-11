# 🔬 LocalResearcherAI

<p align="center">
  <img src="architecture.png" alt="LocalResearcherAI Architecture" width="100%">
</p>

<p align="center">
  <strong>Don't just ask AI. Understand why it answered.</strong>
  <br />
  <strong>Private by default. Transparent by design.</strong>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.12+"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/Local--First-100%25-22c55e?style=for-the-badge" alt="Local First">
  <img src="https://img.shields.io/badge/Ollama-Ready-000000?style=for-the-badge" alt="Ollama Ready">
</p>

---

## What is LocalResearcherAI?

LocalResearcherAI is a local-first AI research assistant that analyzes documents on your own machine using local LLMs.

It is designed around one principle:

> Every answer should make clear what it is based on.

If no files are provided, it uses local model knowledge and clearly labels the answer as unverified.  
If files are provided, it switches into evidence mode and analyzes your documents locally.

Your documents never leave your computer.

---

## Why It Exists

Most AI tools produce answers without making the source of the answer clear.

LocalResearcherAI separates two very different situations:

| Mode | Source | Confidence | Best For |
|---|---|---:|---|
| 🧠 Knowledge Mode | Local model knowledge | Low | Quick explanations |
| 🔬 Evidence Mode | Your documents | Medium-High | Document-backed analysis |

This makes the system honest about what it knows, what it used, and what it cannot verify.

---

## Highlights

| Capability | Status | Description |
|---|---:|---|
| 🔒 Local-first execution | ✅ Ready | Runs locally with Ollama |
| 📄 Document analysis | ✅ Ready | PDF, Markdown and TXT support |
| 🧠 Multi-agent workflow | ✅ Ready | Planner, Researcher, Analyst, Critic and Writer |
| 🔍 Intent detection | ✅ Ready | Routes greetings, small talk and research queries |
| 🧾 Knowledge Mode | ✅ Ready | Clearly marks model-only answers as unverified |
| 🔬 Evidence Mode | ✅ Ready | Uses provided documents with RAG |
| ⚠️ Transparent limitations | ✅ Ready | Does not pretend to have sources it does not have |
| 📌 Evidence attribution | 📅 Planned | Phase 2 |
| 📊 Per-claim confidence | 📅 Planned | Phase 2 |
| 🌐 Web search | 📅 Planned | Future phase |

---

## Quick Start

bash git clone https://github.com/serkannkara/LocalResearcherAIAgent.git cd LocalResearcherAIAgent ./install.sh 

Pull the local models:

bash ollama pull qwen2.5:latest ollama pull nomic-embed-text:latest 

Run your first query:

bash localresearcher ask "What is Agentic AI?" 

Analyze your own document:

bash localresearcher ask "Summarize this document and extract key insights." --files ./your-document.md 

---

## Example Output

text 🔬 LocalResearcherAI  Query: What is Agentic AI? Model: qwen2.5:latest Files: 0  🧠 Detecting intent... ✓ Research intent detected  🧠 Knowledge Mode No documents provided. No web search available. No external evidence.  This is an AI-generated explanation, not verified research. For verifiable results, provide documents.  ✓ Report saved to: reports/report.md 

---

## How It Works

text User Query    │    ▼ Intent Classifier    │    ├── Greeting / Small Talk ──► Quick Reply    │    └── Research           │           ▼    Workflow State Manager           │           ▼ Planner → Researcher → Analyst → Critic → Writer           │           ▼    RAG Layer    ├── Document Loader    ├── Chunker    ├── Embeddings    └── Vector Store           │           ▼       Ollama / Qwen           │           ▼    Markdown Report 

---

## The 5-Agent Pipeline

| Agent | Role |
|---|---|
| Planner | Breaks the user request into a structured research plan |
| Researcher | Retrieves relevant information from documents or model knowledge |
| Analyst | Synthesizes findings and identifies patterns |
| Critic | Reviews gaps, weak reasoning and missing perspectives |
| Writer | Generates the final markdown report |

---

## Knowledge Mode vs Evidence Mode

### 🧠 Knowledge Mode

Used when no files are provided.

bash localresearcher ask "Compare RAG, MCP and Agentic AI" 

The system clearly states:

text No documents provided. No web search available. No external evidence. This is an AI-generated explanation, not verified research. 

### 🔬 Evidence Mode

Used when files are provided.

bash localresearcher ask "Summarize findings" --files report.pdf 

Multiple files can be passed by repeating --files:

bash localresearcher ask "Compare these reports" --files Q1.pdf --files Q2.pdf 

Glob patterns are supported:

bash localresearcher ask "Analyze all notes" --files "./documents/*.md" 

---

## Architecture

### Workflow State

The workflow state is the single source of truth during execution.

text WorkflowState │ ├─ Task │  └─ Original query + documents │ ├─ Current Step │  └─ Planning / Research / Analysis / Critique / Writing │ ├─ Planner Output ├─ Research Findings ├─ Analysis ├─ Critique ├─ Final Report │ └─ Agent Outputs    └─ Complete audit trail 

This enables transparency, debugging and future replay/export features.

### Technology Stack

| Layer | Technology |
|---|---|
| CLI | Typer + Rich |
| LLM | Ollama |
| Default model | qwen2.5 |
| Embeddings | nomic-embed-text |
| Vector DB | ChromaDB |
| Document loading | pypdf, Markdown, TXT |
| Reports | Markdown |

---

## Performance

Typical local performance on Apple Silicon:

| Task | Typical Time |
|---|---:|
| Intent detection | < 0.5s |
| Document loading | 1-2s |
| Vector retrieval | < 300ms |
| Full multi-agent run | seconds to tens of seconds |

Performance depends on hardware, model size and document length.

---

## Roadmap

| Phase | Focus | Status |
|---|---|---:|
| Phase 1 | Local multi-agent MVP | ✅ Complete |
| Phase 2 | Evidence attribution + confidence | 📅 Planned |
| Phase 3 | Enhanced RAG + memory | 📅 Planned |
| Phase 4 | Web UI + workspaces | 📅 Future |
| Phase 5 | Web search integration | 📅 Future |
| Phase 6 | MCP ecosystem | 📅 Vision |

See ROADMAP_PRAGMATIC.md for details.

---

## Future: Explainability Engine

Planned for Phase 2:

markdown ## Conclusion  Local AI adoption is accelerating.  ## Evidence  1. Source: market-report.pdf, page 12    Confidence: 95%  2. Source: industry-blog.md    Confidence: 67%  ## Reasoning Chain  1. Identified theme across documents 2. Cross-referenced supporting evidence 3. Checked for contradictions 4. Weighted by source reliability 

This is not fully available yet. It is part of the roadmap.

---

## Use Cases

bash # Academic research localresearcher ask "Summarize these papers" --files paper1.pdf --files paper2.pdf  # Business analysis localresearcher ask "Analyze this quarterly report" --files Q1.pdf  # Legal review localresearcher ask "Identify key risks in this contract" --files contract.pdf  # Personal knowledge management localresearcher ask "Summarize my notes" --files "./notes/*.md" 

---

## Earning “ResearchOS”

We do not call this ResearchOS yet.

That name is earned, not claimed.

Current: LocalResearcherAI  
Transparent local document research.

Future: ResearchOS  
An operating system for knowledge work.

How we earn it:

- Build trust through transparency
- Deliver explainability at scale
- Add persistent workspaces
- Create plugin and MCP ecosystem
- Prove value with real users

Until then:

Stay focused. Build trust. Deliver value.

---

## Documentation

- Quick Start
- Architecture
- Roadmap
- Contributing
- Vision

---

## Contributing

Contributions are welcome.

Good first issues:

- Add new document format loaders
- Improve error messages
- Add tests
- Write tutorials
- Improve examples

---

## License

MIT License. See LICENSE for details.

---

## Acknowledgments

Built with:

- Ollama — local LLM inference
- ChromaDB — vector database
- Typer — CLI framework
- Rich — terminal UI

---

<p align="center">
  <strong>Made with ❤️ by Serkan Kara</strong>
  <br />
  <br />
  ⭐ Star the project if you find it useful.
</p
