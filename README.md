# Oselot

**Comprehensive autonomous AI-powered OSINT agent**

Oselot is an intelligent OSINT (Open Source Intelligence) agent that automates reconnaissance workflows using a coordinated team of specialized AI agents. It maps an organization's external attack surface by discovering subdomains, resolving network boundaries, fingerprinting technologies, and generating actionable intelligence reports.

Built with [Agno](https://docs.agno.com) for multi-agent orchestration.

---

## How It Works

Oselot uses a hierarchical agent team coordinated by a Manager agent that delegates tasks through an **OSINT Kill Chain**:

```
Scope Definition ──> Asset Discovery ──> Service Validation ──> Reporting
   (ASN Agent)        (BBOT Agent)         (HTTPX Agent)       (Reporter)
```

| Agent | Role | Tool |
|-------|------|------|
| **ASN Specialist** | Maps organizations/domains to ASNs and IP ranges (CIDRs) | [asnmap](https://github.com/projectdiscovery/asnmap) |
| **Subdomain Enumeration Specialist** | Recursive subdomain discovery, DNS permutation, cloud enumeration | [bbot](https://github.com/blacklanternsecurity/bbot) |
| **Web Fingerprinting Agent** | Liveness checking, technology detection, title extraction | [httpx](https://github.com/projectdiscovery/httpx) |
| **OSINT Reporter** | Synthesizes raw data into structured attack surface reports | - |

The Manager agent orchestrates all four in sequence, ensuring each phase feeds into the next.

---

## Installation

### Prerequisites

- Python 3.11+
- The following CLI tools must be installed separately:
  - [asnmap](https://github.com/projectdiscovery/asnmap) - ASN/CIDR mapping
  - [bbot](https://github.com/blacklanternsecurity/bbot) - Subdomain enumeration
  - [httpx](https://github.com/projectdiscovery/httpx) (ProjectDiscovery) - Web probing

### Install Oselot

```bash
git clone https://github.com/0xJaeg3r/OOSEC-Oselot.git
cd oselot
pip install -e .
```

### Configure API Keys

Copy the example environment file and add your keys:

```bash
cp env.example .env
```

Edit `.env` with your API keys:

```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
PDCP_API_KEY=...        # Optional: ProjectDiscovery Cloud Platform
SHODAN_API_KEY=...      # Optional: Shodan integration
```

Oselot supports multiple LLM providers. Set the key for your chosen provider:

| Provider | Environment Variable | Get a Key |
|----------|---------------------|-----------|
| OpenAI | `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com/api-keys) |
| Anthropic | `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) |
| Google | `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com) |

---

## Usage

### CLI

```bash
oselot
```

Or run directly:

```bash
python ocelot_cli.py
```

#### CLI Options

```bash
oselot --model gpt-5.2          # Specify model
oselot --memory                  # Enable conversation memory
oselot --storage                 # Enable persistent agent state
oselot --mcp                     # Enable MCP server support
```

#### CLI Commands

| Command | Description |
|---------|-------------|
| `/model` | Switch between AI models |
| `/memory` | Toggle conversation memory on/off |
| `/storage` | Toggle agent storage/state persistence |
| `/mcp` | Toggle MCP server support |
| `/add-mcp` | Add a Model Context Protocol server |
| `/status` | Show current session configuration |
| `/clear` | Clear the terminal screen |
| `/help` | Show detailed help |
| `/quit` | Exit the CLI |

### Example Tasks

```
> Enumerate subdomains for example.com
> Find ASN and IP ranges for "Acme Corp"
> Probe discovered subdomains for live hosts and technologies
> Perform full OSINT reconnaissance on example.com and generate a report
```

### Programmatic Usage

```python
from agent import OsintAgentSystem

system = OsintAgentSystem(model_name="gpt-5.2")

system.run_assessment("""
1. Perform subdomain enumeration on example.com
2. Extract live hosts
3. Detect technologies running on those hosts
""")
```

---

## Supported Models

### OpenAI
- `gpt-5.2` (default) - Flagship model
- `gpt-5` - Base model
- `o3` / `o3-mini` - Reasoning models

### Anthropic
- `claude-opus-4-6` - Most capable
- `claude-sonnet-4-5` - Fast

### Google
- `gemini-3-pro` - Most intelligent
- `gemini-3-flash` - Fast
- `gemini-2.5-pro` - 1M context

Any other model ID is routed through [LiteLLM](https://docs.litellm.ai/docs/providers) (100+ providers).

---

## Project Structure

```
oselot/
├── agent.py          # Agent system: model selection, team creation, tool wiring
├── ocelot_cli.py     # Interactive CLI with commands and session management
├── prompt.py         # Specialized prompts for each agent
├── tools.py          # OSINT tool wrappers (asnmap, bbot, httpx, CLI utilities)
├── pyproject.toml    # Package configuration and dependencies
├── env.example       # Environment variable template
└── README.md
```

---

## MCP Server Support

Oselot supports [Model Context Protocol](https://modelcontextprotocol.io/) servers for extending agent capabilities. Enable with `/mcp` and add servers with `/add-mcp`.

Built-in presets:
- **Filesystem** - Local file and directory access
- **Git** - Repository reading and search
- **Memory** - Persistent knowledge graph
- **Fetch** - Web content fetching
- **Context7** - Library documentation

Custom command-based or URL-based MCP servers are also supported.

---

## Storage and Memory

| Feature | Purpose | Database |
|---------|---------|----------|
| **Memory** | Stores conversation history for cross-session context | `~/.ocelot/ocelot_agents.db` |
| **Storage** | Persists agent state and internal data | `~/.ocelot/agent_storage.db` |

Both are disabled by default. Enable via CLI flags (`--memory`, `--storage`) or commands (`/memory`, `/storage`).

---

## License

MIT

---

## Authors

00SEC Ghana
