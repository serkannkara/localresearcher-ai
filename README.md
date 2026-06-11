// # 🔬 LocalResearcherAI
// 
// **Don't just ask AI. Understand why it answered.**
// 
// **Private by default. Transparent by design.**
// 
// <p align="center">
//   <img src="docs/images/architecture.png" alt="LocalResearcherAI Architecture" width="100%">
// </p>
// 
// A local-first, explainable document research system focused on transparency and trust.  
// **Your documents never leave your computer.**
// 
// [![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
// [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
// [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
// 
// ---
// 
// ## ✨ Why People Like LocalResearcherAI
// 
// - 🔒 **100% Local Processing** - No API keys, no cloud, complete privacy
// - 🧠 **Multi-Agent Research Pipeline** - 5 specialized agents working together
// - 📄 **RAG-Powered Document Analysis** - Evidence-backed insights from your files
// - 🔍 **Transparent Modes** - Clear separation between knowledge vs evidence
// - ⚠️ **Honest About Limitations** - Never pretends to have sources it doesn't
// - 📝 **Beautiful Markdown Reports** - Professional output, fully customizable
// 
// ---
// 
// ## 🎯 Why This Project?
// 
// **The Problem**: AI tools are black boxes. You get answers but don't know why.
// 
// **Our Solution**: A transparent, local-first research system that shows you its reasoning.
// 
// ### What Works Today (v0.1.0)
// 
// | Feature | Status | Notes |
// |---------|--------|-------|
// | **Local-first** | ✅ Ready | 100% local processing, no cloud |
// | **Document analysis** | ✅ Ready | PDF, Markdown, TXT support |
// | **Multi-agent pipeline** | ✅ Ready | 5 specialized agents working together |
// | **Intent detection** | ✅ Ready | Smart routing based on query type |
// | **Mode separation** | ✅ Ready | Clear distinction between knowledge vs evidence |
// | **Transparent limitations** | ✅ Ready | Honest about what sources are used |
// | **Explainable workflows** | 🚧 In Progress | Step-by-step agent execution visible |
// | **Per-claim confidence** | 📅 Planned | Phase 2 (see roadmap) |
// | **Evidence attribution** | 📅 Planned | Phase 2 (see roadmap) |
// | **Web search** | 📅 Planned | Phase 3 (see roadmap) |
// 
// **Legend**: ✅ Ready | 🚧 In Progress | 📅 Planned
// 
// ---
// 
// ## ⚡ Quick Start
// 
// ```bash
// # 1. Clone and install
// git clone https://github.com/serkannkara/LocalResearcherAI.git
// cd LocalResearcherAI
// ./install.sh
// 
// # 2. Pull models (one-time setup)
// ollama pull qwen2.5:latest
// ollama pull nomic-embed-text:latest
// 
// # 3. Run your first query
// localresearcher ask "Summarize key findings" --files examples/sample.md
// ```
// 
// **Expected time**: Typically within seconds to tens of seconds depending on your hardware and model.
// 
// ---
// 
// ## 🎬 How It Works
// 
// ### Two Modes: Knowledge vs Evidence
// 
// **The key difference that makes us transparent:**
// 
// | Mode | Source | Speed | Confidence | Use Case |
// |------|--------|-------|------------|----------|
// | 🧠 **Knowledge** | Model's training data | Fast | 🔴 LOW | Quick explanations |
// | 🔬 **Evidence** | Your documents | Normal | 🟢 HIGH | Verified research |
// 
// ### 🧠 Knowledge Mode (No Documents)
// 
// **Model knows → General explanation**
// 
// - Uses LLM's internal knowledge
// - Fast responses
// - Clearly marked as "not verified research"
// - **Confidence: LOW**
// 
// ```bash
// localresearcher ask "What is Agentic AI?"
// # → Quick explanation from model knowledge
// # → Clearly marked with limitations
// ```
// 
// ### 🔬 Evidence Mode (With Documents)
// 
// **Documents prove → Evidence-backed analysis**
// 
// - Analyzes your provided documents
// - RAG-based retrieval
// - Evidence-aware responses
// - **Confidence: MEDIUM-HIGH**
// 
// ```bash
// # Analyze a single document
// localresearcher ask "Summarize findings" --files report.pdf
// 
// # Analyze multiple documents
// localresearcher ask "Compare these reports" --files Q1.pdf Q2.pdf
// 
// # Use glob patterns
// localresearcher ask "Analyze all docs" --files ./documents/*.md
// ```
// 
// **Note**: Repository analysis is planned for Phase 3. Currently, use --files for document analysis.
// 
// ---
// 
// ## 🏗️ Architecture
// 
// <p align="center">
//   <img src="docs/images/architecture.png" alt="System Architecture" width="90%">
// </p>
// 
// ### 5-Agent Pipeline
// 
// **What each agent does:**
// 
// 1. **🗓️ Planner** - Breaks down the research task into steps
// 2. **🔍 Researcher** - Retrieves relevant information (RAG if documents available)
// 3. **📊 Analyst** - Analyzes and synthesizes findings
// 4. **🛡️ Critic** - Evaluates quality and identifies gaps
// 5. **✍️ Writer** - Generates final markdown report
// 
// All agents share state through **WorkflowState** for complete transparency.
// 
// ---
// 
// ## 📊 Performance Benchmarks
// 
// **Test Environment**: MacBook Air M2, 16GB RAM
// 
// | Task | Time | Details |
// |------|------|---------|
// | **Intent Detection** | <0.5s | Pattern matching + LLM fallback |
// | **Load 100-page PDF** | 1.8s | pypdf extraction |
// | **Generate Embeddings** | 4.2s | nomic-embed-text |
// | **RAG Retrieval** | 180ms | ChromaDB similarity search |
// | **Full Pipeline** | ~20s | End-to-end with all agents |
// | **RAM Peak** | 5.3GB | Includes model |
// 
// **Note**: Results vary depending on hardware and model size.
// 
// **Model**: qwen2.5:7b (4.7GB)  
// **Vector DB**: ChromaDB (persistent)  
// **Embedding**: nomic-embed-text (274MB)
// 
// ---
// 
// ## 🌟 What Makes Us Different
// 
// ### Transparency First
// 
// **We don't pretend to have sources we don't have.**
// 
// **Knowledge Mode** clearly states:
// - ❌ No external documents
// - ❌ No citations available
// - ❌ Information may be outdated
// - 🔴 Confidence: LOW
// 
// **Evidence Mode** clearly shows:
// - ✅ Documents analyzed
// - ✅ RAG-based retrieval
// - ✅ Source-aware responses
// - 🟢 Confidence: MEDIUM-HIGH
// 
// ### Honest About Limitations
// 
// ```markdown
// ⚠️  Knowledge Mode Notice
// 
// This response was generated from the language model's 
// internal knowledge.
// 
// - ❌ No external documents were analyzed
// - ❌ No evidence citations available
// - ❌ Information may be outdated
// 
// Confidence Level: LOW
// ```
// 
// This honesty is **rare** in AI tools.
// 
// ---
// 
// ## 🚀 Future: Explainability (Phase 2)
// 
// ### What's Coming (Not Yet Available)
// 
// ```markdown
// ## Conclusion: Local AI adoption is accelerating
// 
// ### Evidence:
// 1. ✅ **Source**: market-report.pdf (Page 12)
//    - Quote: "65% of enterprises prioritizing on-premise AI"
//    - **Confidence: 95%**
//    - Weight: High
// 
// 2. ⚠️  **Source**: industry-blog.md
//    - Quote: "Local models gaining traction"
//    - **Confidence: 67%**
//    - Weight: Low
// 
// ### Overall Confidence: 93%
// 
// ### Reasoning Chain:
// 1. Identified theme across documents
// 2. Cross-referenced data sources
// 3. Validated statistical claims
// 4. Weighted by source reliability
// ```
// 
// **Status**: 🚧 Planned for Phase 2 (Evidence Attribution & Confidence Scoring)
// 
// See [ROADMAP.md](ROADMAP.md) for details.
// 
// ---
// 
// ## 🎯 Roadmap
// 
// | Phase | Focus | Status |
// |-------|-------|--------|
// | **Phase 1** | MVP - Multi-agent pipeline | ✅ Complete |
// | **Phase 2** | Evidence attribution + Confidence | 📅 Planned |
// | **Phase 3** | Enhanced RAG + Memory | 📅 Planned |
// | **Phase 4** | Web UI + Workspaces | 📅 Future |
// | **Phase 5** | Web search integration | 📅 Future |
// | **Phase 6** | MCP ecosystem | 📅 Vision |
// 
// **Full details**: [ROADMAP_PRAGMATIC.md](ROADMAP_PRAGMATIC.md)
// 
// ---
// 
// ## 🏆 Use Cases
// 
// ### Academic Research
// - Analyze multiple papers
// - Generate literature summaries
// - Find contradictions across sources
// 
// ### Business Analysis
// - Quarterly report analysis
// - Market research synthesis
// - Competitive intelligence
// 
// ### Legal Review
// - Contract analysis
// - Document comparison
// - Evidence organization
// 
// ### Personal Knowledge Management
// - Organize research notes
// - Synthesize learning materials
// - Build knowledge base
// 
// ---
// 
// ## 💎 First Experience
// 
// We obsess over your first 5 minutes:
// 
// **Minute 1**: Clone and run `./install.sh`  
// **Minute 2**: Ollama pulls models (automatic)  
// **Minute 3**: Test with `localresearcher ask "Hello"`  
// **Minute 4**: Try with a document: `--files examples/sample.md`  
// **Minute 5**: Explore your first report in `reports/`  
// 
// **If you're not impressed in 5 minutes, we failed.**
// 
// ---
// 
// ## 🚀 Earning "ResearchOS"
// 
// We don't call it "ResearchOS" yet. That name is **earned**, not claimed.
// 
// **Current (v0.1.0)**: LocalResearcherAI  
// → "Transparent local document research"
// 
// **Future (v2.0.0)**: ResearchOS  
// → "Operating system for knowledge work"
// 
// **How we earn it**:
// - ✅ Build trust through transparency
// - ✅ Deliver explainability at scale
// - ✅ Create plugin ecosystem
// - ✅ Enable team collaboration
// - ✅ Prove value with real users
// 
// Until then: **Stay focused. Build trust. Deliver value.**
// 
// See [VISION_2.0.md](VISION_2.0.md) for the long-term vision.
// 
// ---
// 
// ## 🎤 One-Line Pitch
// 
// **"Local-first, transparent AI research. Know why, not just what."**
// 
// ---
// 
// ## 📖 Documentation
// 
// - [Quick Start](docs/QUICKSTART.md)
// - [Architecture](docs/ARCHITECTURE.md)
// - [Roadmap](ROADMAP_PRAGMATIC.md)
// - [Contributing](CONTRIBUTING.md)
// - [Vision](VISION_2.0.md)
// 
// ---
// 
// ## 🤝 Contributing
// 
// We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
// 
// **Good first issues**:
// - Add new document format loaders
// - Improve error messages
// - Write tutorials
// - Add tests
// 
// ---
// 
// ## 📄 License
// 
// MIT License - see [LICENSE](LICENSE) for details.
// 
// ---
// 
// ## 🙏 Acknowledgments
// 
// Built with:
// - [Ollama](https://ollama.ai/) - Local LLM inference
// - [ChromaDB](https://www.trychroma.com/) - Vector database
// - [Typer](https://typer.tiangolo.com/) - CLI framework
// - [Rich](https://rich.readthedocs.io/) - Terminal UI
// 
// ---
// 
// **Made with ❤️ by the LocalResearcherAI team**
// 
// ⭐ Star us on GitHub if you find this useful!