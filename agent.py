import os
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
from agno.models.google import Gemini
from agno.team.team import Team
from agno.tools.tavily import TavilyTools
from agno.tools.file import FileTools
from tools import OSINT_TOOLS
from agno.tools.mcp import MultiMCPTools, MCPTools
from prompt import *
load_dotenv()

OCELOT_DIR = Path.home() / ".ocelot"
OCELOT_DIR.mkdir(exist_ok=True)

class OsintAgentSystem:
    """
    Complete and comprehensive OSINT agent with hierarchical delegation.
    Manager coordinates specialized agent for complete recon activity
    """
## Give agent a spec sheet 

    def __init__(
                self,
                 model_name: str = "gpt-5.2",
                 use_memory: bool = False,
                 use_storage: bool = False,
                 use_mcp: bool = False,
                 mcp_servers: Optional[List[Dict]] = None,
                 
                 ):
        
## Give the agent a mind

        self.model_name = model_name 
        self.model = self._get_model(model_name)
        self.use_memory = use_memory
        self.use_storage = use_storage
        self.use_mcp = use_mcp
        self.mcp_servers = mcp_servers or []
        self.mcp_tools = None
            
          
## Give agent base tools
        self.base_tools = [
            TavilyTools(), # Web search but will need an API Key remember
            FileTools(base_dir=Path("."),
                    enable_save_file=True,
                    enable_delete_file=False)
        ]
## Initialize all  tools
        self.all_tools = self._initialize_tools()


## Set up storage
        self.storage_db = None
        if use_storage:
            storage_path = OCELOT_DIR / "agent_storage.db"
            self.storage_db = SqliteDb(db_file=str(storage_path))

#Set up memory
        self.memory_db = None
        if use_memory:
            memory_path = OCELOT_DIR / "ocelot_agents.db"
            self.memory_db = SqliteDb(db_file=str(memory_path))

# Create specialized agents and team        
        self._create_all_agents()
        self._create_osint_team()


##  Create mind for agent - Create model selector
    def _get_model(self, model_id: str):
        """
        Gets the right model based on model id
        """

        if "claude" in model_id.lower():
            return Claude(id=model_id)
        elif "gpt" in model_id.lower() or "o1" in model_id.lower(
        ) or "o3" in model_id.lower():
            return OpenAIChat(id=model_id)
        elif "gemini" in model_id.lower():
            return Gemini(id=model_id)
        else:
            try:
                from agno.models.litellm import LiteLLM
                return LiteLLM(id=model_id, name="LiteLLM")
            except ImportError:
                #Fallback to OpenAI
                return OpenAIChat(id=model_id)
            
## Create the initialize tools helper function
    def _initialize_tools(self):
        """Initialize tools including MCP Servers (Optional)"""
        tools = OSINT_TOOLS + self.base_tools

        # Add MCP tools if enabled and servers configured
        if self.use_mcp and self.mcp_servers:
            try:
                #Separate command-based and URL-based servers
                commands = []
                url_servers = []

                for server in self.mcp_servers:
                    if 'command' in server:
                        commands.append(server['command'])
                    elif 'url' in server:
                        url_servers.append(server)

                # Add command-based servers via MultiMCPTools
                if commands:
                    self.mcp_tools = MultiMCPTools(commands)
                    tools.append(self.mcp_tools)

                #Add URL-based servers individually
                for url_server in url_servers :
                    try:
                        mcp_tool = MCPTools(
                            url=url_server['url'],
                            transport=url_server.get('transport','streamable-http')
                        )
                        tools.append(mcp_tool)
                    except Exception as e:
                        print(
                            f"Warning: Failed to initialize MCP Server {url_server.get('name', 'unknown')}: {e}"
                        )

            except Exception as e:
                print (f" Warning: Failed to initialize MCP tools: {e}")
            
        return tools
    
    def _create_all_agents(self):
        """
        Creates all specialized OSINT agents with their tools and prompts
        """

        agent_kwargs = {
            "model": self.model,
            "tools": self.all_tools
        }

        # Add storage databse if enabled
        if self.storage_db:
            agent_kwargs["db"] = self.storage_db
            agent_kwargs["add_history_to_context"] = True

        # Add memory on top of storage if enabled
        if self.memory_db:
            agent_kwargs["db"] = self.memory_db
            agent_kwargs["enable_user_memories"] = True
            agent_kwargs["add_history_to_context"] = True
        
        #Create specialized Agents

        self.asn_agent = Agent(
            name="ASN Specialist",
            role="Specializes in converting organization names to IP ranges",
            instructions=[ASNMAP_AGENT_PROMPT],
            **agent_kwargs,
        )

        self.bbot_agent = Agent(
            name="Subdomain Enumeration Specialist",
            role="Specializes in finding subdomains of organizations",
            instructions=[BBOT_RECON_AGENT_PROMPT],
            **agent_kwargs,
        )

        self.httpx_agent = Agent(
            name="Subdomain Status verification Agent",
            role="Checks if detected subdomains are alive and finds the technology they are running on",
            instructions=[HTTPX_FINGERPRINT_AGENT_PROMPT],
            **agent_kwargs,
        )

        self.reporting_agent = Agent(
            name="OSINT Reporter",
            role="OSINT Documentation",
            instructions=[OSINT_REPORTING_AGENT_PROMPT],
            **agent_kwargs,
        )

    def _create_osint_team(self):
        """ Create the hierarchical OSINT team with manager coordination"""
        import uuid

        #Create persistent session ID to maintain context accross multiple ineteractions
        self.session_id = str(uuid.uuid4())

        # Team configuration - always add history to context for persistent conversion
        team_kwargs = {
            "name":"OSINT Team",
            "model": self.model,
            "respond_directly": False,
            "members": [
                self.asn_agent,
                self.bbot_agent,
                self.httpx_agent,
                self.reporting_agent
            ],
            "markdown": True,
            "instructions": [OSINT_MANAGER_AGENT_PROMPT],
            "show_members_responses": True,
            "add_history_to_context": True, # CRITICAL: ALways preserve conversation history
            "debug_mode": True,
            "debug_level": 2,

        }

        #Add memory to database if enabled (for persistent storage accross sessions)
        if self.memory_db:
            team_kwargs["db"] = self.memory_db
            team_kwargs["enable_user_memories"]= True
        
        self.osint_team = Team(**team_kwargs)
    
    def run_assessment(self, task: str, stream: bool = True, show_full_reasoning: bool = True, stream_events:bool = True):
        """Conduct an OSINT task with persistent session context"""
        # Use persistent session_id to maintain context across multiple runs
        self.osint_team.print_response(
            task,
            stream=stream,
            session_id=self.session_id,
            show_full_reasoning=show_full_reasoning,
            stream_events=stream_events
        )
    
    def get_agent(self, agent_type:  str):
        """Get a specific agent by type"""
        agents = {
            "asn": self.asn_agent,
            "bbot": self.bbot_agent,
            "httpx":self.httpx_agent,
            "reports":self.reporting_agent
        }
        return agents.get(agent_type.lower())

def main():
    """Main execution example"""
    print("\n Initializing OSINT Agent System...\n")

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not found!")
        print("\nPlease set your OpenAI API key:")
        print("1. Copy .env.example to .env")
        print("2. Add your API key to the .env file")
        print("3. Get an API key from: https://platform.openai.com/api-keys\n")
        return

    # Create security system
    system = OsintAgentSystem(model_name="gpt-5.2")
    example_task = """
    1.perform subdomain enumeration on csa.gov.gh
    2.Extract live hosts
    3.Detect technologies running on those hosts 

    """ 

    system.run_assessment(example_task, stream=True, show_full_reasoning=True, stream_events=True)

if __name__ == "__main__":
    main()


