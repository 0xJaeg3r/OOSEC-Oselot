# ocelot_cli.py Fixes

## Fix 1: CrossBow → Ocelot branding
- Line 85: `Exit the CrossBow Agent CLI` → `Exit the Ocelot CLI`
- Line 113: `~/.crossbow/crossbow_agents.db` → `~/.ocelot/ocelot_agents.db`
- Line 117: `~/.crossbow/agent_storage.db` → `~/.ocelot/agent_storage.db`
- Line 328: `~/.crossbow/crossbow_agents.db` → `~/.ocelot/ocelot_agents.db`
- Line 332: `~/.crossbow/agent_storage.db` → `~/.ocelot/agent_storage.db`
- Line 384: `CrossBow Security Agent` → `Ocelot OSINT Agent`
- Line 416: `CrossBow agent` → `Ocelot agent`

## Fix 2: Sync model list in get_model_input() with print_help()
- Replace outdated models (gpt-4o-mini, gpt-4-turbo, etc.) with current ones from print_help()
- Update default model from `gpt-4o-mini` to `gpt-5.2` (matching agent.py)

## Fix 3: Fix /status output to reflect actual agents and tools
- Change "16 Security Specialists" → "4 OSINT Specialists"
- Replace tool list with actual tools: asnmap, bbot, httpx, Tavily, FileTools

## Fix 4: Fix /help capabilities section to reflect actual tools
- Remove references to nmap, netcat, bandit, semgrep, nuclei, Julia Browser, DuckDuckGo
- List actual capabilities: ASN mapping, subdomain enumeration, web fingerprinting, web search, file operations

## Fix 5: API key check — support multiple providers
- Instead of requiring only OPENAI_API_KEY, check for the relevant key based on the selected model
- Or remove the hard exit and let initialization fail with a clear error instead

## Fix 6: Default model mismatch
- Line 391: change default from `gpt-4o-mini` to `gpt-5.2` (matching agent.py)
