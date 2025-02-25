import json
import os
from typing import Dict, Any

class MemoryManager:
    def __init__(self, project_path: str):
        self.memory_dir = os.path.join(project_path, ".crewai_memories")
        os.makedirs(self.memory_dir, exist_ok=True)

    def save_memory(self, agent_name: str, memory: Dict[str, Any]) -> None:
        """Save agent memory to file"""
        memory_file = os.path.join(self.memory_dir, f"{agent_name}.json")
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(memory, f, indent=2)

    def load_memory(self, agent_name: str) -> Dict[str, Any]:
        """Load agent memory from file"""
        memory_file = os.path.join(self.memory_dir, f"{agent_name}.json")
        if not os.path.exists(memory_file):
            return {}
        
        with open(memory_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def clear_memory(self, agent_name: str) -> None:
        """Clear agent memory"""
        memory_file = os.path.join(self.memory_dir, f"{agent_name}.json")
        if os.path.exists(memory_file):
            os.remove(memory_file)
