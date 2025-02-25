import asyncio
import os
from dotenv import load_dotenv
from crewai import Crew, Process
from .agents.supervisor_agent import SupervisorAgent
from .agents.prompt_agent import PromptAgent
from .agents.code_agent import CodeAgent
from .agents.test_agent import TestAgent
from .agents.documentation_agent import DocumentationAgent
from .agents.review_agent import ReviewAgent
from .tools.file_operations import FileOperations
from .ipc.message_handler import MessageHandler, WebSocketServer

# Load environment variables
load_dotenv()

class Backend:
    def __init__(self):
        self.workspace_path = os.getenv('WORKSPACE_PATH', os.getcwd())
        self.host = os.getenv('HOST', 'localhost')
        self.port = int(os.getenv('PORT', 3000))
        
        # Initialize agents and crew
        self.setup_agents()
        
    def setup_agents(self):
        """Initialize all agents and set up the development crew"""
        try:
            # Create file operations tool
            file_ops = FileOperations(self.workspace_path)

            # Create prompt engineering agent
            self.prompt_agent = PromptAgent(
                name="prompt_agent",
                project_path=self.workspace_path
            )
            self.prompt_agent.add_tool(file_ops)

            # Create specialized development agents
            self.code_agent = CodeAgent(
                name="code_agent",
                project_path=self.workspace_path
            )
            self.code_agent.add_tool(file_ops)

            self.test_agent = TestAgent(
                name="test_agent",
                project_path=self.workspace_path
            )
            self.test_agent.add_tool(file_ops)

            self.doc_agent = DocumentationAgent(
                name="doc_agent",
                project_path=self.workspace_path
            )
            self.doc_agent.add_tool(file_ops)

            self.review_agent = ReviewAgent(
                name="review_agent",
                project_path=self.workspace_path
            )
            self.review_agent.add_tool(file_ops)

            # Create supervisor agent
            self.supervisor = SupervisorAgent(
                name="supervisor_agent",
                project_path=self.workspace_path
            )
            self.supervisor.add_tool(file_ops)

            # Register all agents with supervisor
            self.supervisor.register_agent('prompt', self.prompt_agent)
            self.supervisor.register_agent('code', self.code_agent)
            self.supervisor.register_agent('test', self.test_agent)
            self.supervisor.register_agent('documentation', self.doc_agent)
            self.supervisor.register_agent('review', self.review_agent)

            # Create development crew with prompt agent as first point of contact
            self.crew = Crew(
                agents=[
                    self.prompt_agent.agent,  # First in the chain
                    self.supervisor.agent,    # Coordinates based on prompt analysis
                    self.code_agent.agent,
                    self.test_agent.agent,
                    self.doc_agent.agent,
                    self.review_agent.agent
                ],
                tasks=[],  # Tasks will be created dynamically
                process=Process.hierarchical,  # Use hierarchical process with supervisor
                manager_llm=self.supervisor.agent.llm,  # Use supervisor's LLM for management
                verbose=True,
                max_rpm=10,  # Limit requests per minute
                memory=True,  # Enable crew memory
                cache=True  # Enable caching
            )

            # Initialize message handler with prompt agent and supervisor chain
            self.message_handler = MessageHandler(
                prompt_agent=self.prompt_agent,
                supervisor_agent=self.supervisor
            )
            
            # Initialize WebSocket server
            self.server = WebSocketServer(
                self.host,
                self.port,
                self.message_handler
            )
            
            print("Successfully initialized development crew and agents")
            
        except Exception as e:
            print(f"Error setting up agents: {e}")
            raise

    async def start(self):
        """Start the backend server"""
        try:
            print(f"Starting CrewAI VSCode backend on {self.host}:{self.port}")
            print(f"Workspace path: {self.workspace_path}")
            await self.server.start()
        except Exception as e:
            print(f"Error starting backend: {e}")
            raise

def main():
    """Main entry point"""
    try:
        backend = Backend()
        asyncio.run(backend.start())
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Fatal error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
