#!/bin/bash

# LocalResearcherAI - Quick Run Script
# Bu script projeyi hızlıca çalıştırmanızı sağlar

set -e

echo "🔬 LocalResearcherAI - Quick Start"
echo "===================================="
echo ""

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Ollama kontrolü
echo "1️⃣  Checking Ollama..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Ollama is running${NC}"
else
    echo -e "${RED}❌ Ollama is not running${NC}"
    echo -e "${YELLOW}Please start Ollama in another terminal:${NC}"
    echo "   ollama serve"
    exit 1
fi

# 2. Model kontrolü
echo ""
echo "2️⃣  Checking models..."
if ollama list | grep -q "qwen2.5"; then
    echo -e "${GREEN}✅ qwen2.5 model found${NC}"
else
    echo -e "${YELLOW}⚠️  qwen2.5 model not found${NC}"
    echo "Pulling model..."
    ollama pull qwen2.5:latest
fi

if ollama list | grep -q "nomic-embed-text"; then
    echo -e "${GREEN}✅ nomic-embed-text model found${NC}"
else
    echo -e "${YELLOW}⚠️  nomic-embed-text model not found${NC}"
    echo "Pulling model..."
    ollama pull nomic-embed-text:latest
fi

# 3. Virtual environment kontrolü
echo ""
echo "3️⃣  Checking virtual environment..."
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment exists${NC}"
fi

# 4. Virtual environment aktifleştir
echo ""
echo "4️⃣  Activating virtual environment..."
source venv/bin/activate

# 5. Kurulum kontrolü
echo ""
echo "5️⃣  Checking installation..."
if ! command -v localresearcher &> /dev/null; then
    echo -e "${YELLOW}⚠️  Installing LocalResearcher...${NC}"
    pip install --upgrade pip > /dev/null
    pip install -e . > /dev/null
    echo -e "${GREEN}✅ Installation complete${NC}"
else
    echo -e "${GREEN}✅ LocalResearcher is installed${NC}"
fi

# 6. Version göster
echo ""
echo "6️⃣  Version info:"
localresearcher version

# 7. Kullanım talimatları
echo ""
echo "===================================="
echo "✅ All checks passed! Ready to use."
echo "===================================="
echo ""
echo "📖 Example commands:"
echo ""
echo "  # Simple query:"
echo "  localresearcher ask \"What are AI trends?\""
echo ""
echo "  # With document:"
echo "  localresearcher ask \"Summarize this\" --files examples/sample.md"
echo ""
echo "  # Multiple files:"
echo "  localresearcher ask \"Compare these\" --files doc1.pdf doc2.pdf"
echo ""
echo "🎯 Quick test:"
echo "  localresearcher ask \"What is local-first AI?\" --files examples/sample.md"
echo ""

# 8. Kullanıcıya sor
read -p "Run quick test now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 Running test query..."
    echo ""
    localresearcher ask "What are the key trends mentioned in this document?" --files examples/sample.md
fi

echo ""
echo "✨ Done! Virtual environment is active."
echo "   Type 'deactivate' to exit."