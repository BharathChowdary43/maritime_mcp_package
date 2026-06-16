# Maritime Compliance AI Platform (MCP-RAG & Baseline Engine)

An enterprise-grade, multi-agent compliance validation platform engineered to ingest, cross-reference, and align maritime regulatory frameworks including **MARPOL Regulations**, **SIRE 2.0 Inspection Checklists**, and **ISM Code Safety Procedures**. 

The platform features a **Dual-Backend Server Architecture**, allowing runtime selection between a deterministic keyword-matching regex baseline and an advanced, fully decoupled Semantic Retrieval-Augmented Generation (RAG) persistent architecture.

---

## 🏗️ The Dual-Backend Server Paradigm

To demonstrate architectural evolution and allow comparative benchmarking, this platform is delivered with two independent Model Context Protocol (MCP) server implementations. Both seamlessly expose identical tool schemas over standardized `stdio` JSON-RPC pipes but operate on completely different internal data layers.

### 1. The Advanced Production Backend (maritime_mcp/server.py):
This server imports a completely isolated, standalone rag/ sub-package. It translates conversational text queries into dense mathematical vector coordinates, executes local cosine similarity distance lookups against a persistent embedded cache database on disk, evaluates confidence scores to drop out-of-domain noise, and wraps grounding evidence inside defensive XML tags to suppress downstream LLM hallucinations.

### 2. The Baseline Substring Backend (maritime_mcp/server_regex.py):
This server executes lookups using a traditional Inverted-Index Regex Boundary Approach. It isolates alphabetic tokens from incoming conversational strings, performs bidirectional substring intersection matches against raw flat JSON text records, and returns hits based on raw character overlaps. This serves as the benchmark foundation to measure the accuracy jump provided by semantic understanding.

---

## 🛠️ Prerequisites & System Requirements
Before initialization, ensure your host assessment machine satisfies the following baseline environmental dependencies:
* **Python Runtime:** version 3.10 or higher
* **Environment Manager:** `uv` (highly recommended for rapid installation) or `pip`

---

# Step-by-Step Scratch Deployment Guide

Follow these exact operational steps to deploy, synchronize, and run the platform from a completely clean directory.

### 1. Target Directory Clone & Structure Check:
Ensure your physical workspace directory matches the structural tree matrix below before executing runtime scripts:

```text
maritime_mcp_package/
│
├── data/                             # Raw Immutable JSON Data Assets
│   ├── marpol_rules.json
│   ├── sire_questions.json
│   └── ism_requirements.json
│
├── maritime_mcp/                     # Protocol Ingress/Egress Gateway
│   ├── client.py                     # LangGraph Multi-Agent Engine
│   ├── server.py                     # Advanced Persistent RAG Backend Server
│   └── server_regex.py               # Baseline Regex Keyword Backend Server
│
├── rag/                              # Isolated Data Math Core Package
│   ├── config.py                     # Global Path Configuration
│   ├── telemetry.py                  # Log Stream Allocator
│   ├── ingestion/                    # Object-Based Chunking & Seeding
│   ├── retrieval/                    # Cosine Similarity Search Engine
│   └── generation/                   # Grounding Prompt Envelope Builder
│
├── .env                              # Local Environment Secrets File
├── setup.py                          # Global Package Dependency Manifest
└── run_tests.py                      # Master Integration Evaluation Suite
```

### 2. Virtual Environment Isolation:
Open a clean command terminal inside the root directory of your project folder and run the following routines to build and activate a clean virtual workspace:

## Create an isolated python virtual environment using uv
```bash
uv venv
```

# Activate the isolated virtual environment
## On Windows Command Prompt:
```bash
.venv\Scripts\activate
```
## On macOS / Linux Terminal:
```bash
source .venv/bin/activate
```

### 3. Editable Package Synchronization:
Instead of executing standalone pip additions, run an editable dependency installation script. This registers your package root folder globally within your active virtual environment path layout and automatically installs all required backend framework libraries (chromadb, sentence-transformers, torch, langgraph, etc.) using your system manifest files as the single source of truth:

```bash
uv pip install -e .
```

(Note: If you run this file setup for the first time, your screen will output a collection list summary showing your packages built successfully.)

### 4. Credentials Setup
Create a file explicitly named .env directly in your root workspace directory and add your Groq network Completion API secret credential key:

```bash
GROQ_API_KEY="your_actual_groq_api_key_here"
```

# Optional: MCP Client Visual Host Integration (Claude Desktop)
To visually verify this system's execution inside an active MCP production environment, you can hook the server directly into your local Claude Desktop application by adding the following block to your sentry-config settings profile file (%APPDATA%\Claude\claude_desktop_config.json on Windows or ~/Library/Application Support/Claude/claude_desktop_config.json on macOS):

```bash
{
  "mcpServers": {
    "maritime-compliance-rag": {
      "command": "python",
      "args": ["-m", "maritime_mcp.server"],
      "env": {
        "PYTHONPATH": "C:/Users/YOUR_USER/PATH_TO_PROJECT/maritime_mcp_package"
      }
    }
  }
}
```

# Core Component Validation Tracing

The platform is engineered with standalone verification files placed inside each processing module layer. This allows you to audit the ingestion, retrieval, and generation code blocks without booting up any network components or consuming API credits.

### Phase 1: Verify Data Ingestion, Textification, and Disk Cache Seeding
Run this diagnostic to test your raw JSON parsing logic and construct your persistent binary vector files:

```bash
python rag/ingestion/validate_ingestion.py
```

**Expected Result:** 
The console will verify the parsing layout and output a summary showing your items loaded successfully. A new directory called rag/embeddings_db/ will be generated containing your local storage files.

**Cache Test:** 
Execute the script a second time. The boot-up latency drops immediately to 0 milliseconds, and your logging logs a series of high-speed [DISK HIT] cache bypass entries.

### Phase 2: Verify Semantic Retrieval & Synonym Translation Math
Run this diagnostic to test how your system handles complex everyday user words that do not literally match the phrasing stored inside the source files:

```bash
python rag/retrieval/validate_retrieval.py
```

**Expected Result:** 
The engine queries your persistent disk, resolves synonyms like "bilge water sludge" against regulatory phrases like "oily mixtures," and returns the exact matching record along with its mathematical Cosine Distance Score.

### Phase 3: Verify Grounding Context Envelope Layout
Run this diagnostic to verify that your prompt context block applies the strict 0.55 distance cut-off score to discard irrelevant text noise, packaging the final payload cleanly inside structured XML grounding boundaries:

```bash
python rag/generation/validate_generation.py
```

# Running the Platform (Global Execution)
Once you have verified your component files locally, you can choose which backend server engine to run and validate against the primary evaluation testing suite.

## 1.Running with the Advanced Semantic RAG Backend (Default)
To execute your test matrix against the full persistent semantic RAG framework, ensure your maritime_mcp/server.py file is referenced as the primary background tool pipeline target, then execute your master integration evaluation suite:

```bash
python run_tests.py
```

**Output Trace:** 
Open the newly populated query_output.json file in your root workspace. Observe how the multi-agent graph effortlessly reads your structured XML context tags to synthesize grounding answers with zero hallucinations.

## 2.Running with the Baseline Regex Keyword Backend
To execute the baseline benchmark to test performance drops or run character matching verifications, adjust your application config launcher to execute maritime_mcp/server_regex.py as your tool server background pipe target, and trigger your evaluation suite:

```bash
python run_tests.py
```

**Output Trace:** Check your query_output.json file. Notice how the regular expression character match breaks completely when faced with synonym-heavy questions or cross-domain topic switches, highlighting the power of the semantic RAG architecture upgrade.

# Deep Observability Telemetry Matrix
If you run into any validation anomalies or need to analyze how your system calculates vector relationships under the hood, open your auto-generated log structures inside rag/logs/:

### ingestion.log:
Tracks the textification mapping process and documents structural data loading sequences.

### retrieval.log:
Traces raw incoming strings, matching indexes, and records the exact calculated Cosine Distance Scores to expose semantic drift.

### generation.log:
Logs the exact structural context envelope injected into the model's context window.
