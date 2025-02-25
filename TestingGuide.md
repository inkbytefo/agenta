# Testing Guide for Agenta with Prompt Engineer Agent

## Setup

1. Ensure all dependencies are installed:
```bash
cd src/backend
pip install -r requirements.txt
```

2. Set up environment variables in `src/backend/.env`:
```env
OPENAI_API_KEY=your_api_key
WORKSPACE_PATH=path_to_your_workspace
HOST=localhost
PORT=3000
```

## Running the System

1. Start the backend server:
```bash
cd src/backend
python main.py
```

2. Launch VS Code extension in debug mode:
- Open project in VS Code
- Press F5 to start debugging
- Extension will activate in a new VS Code window

## Test Cases

### 1. Basic Prompt Analysis

Try this simple request:
```
Create a function to calculate the factorial of a number
```

Expected flow:
1. Prompt Agent will analyze and structure the request
2. You'll see the enhanced prompt with:
   - Technical requirements
   - Required agents (Code, Test, Documentation)
   - Context and constraints

### 2. Complex Task with Multiple Agents

Try a more complex request:
```
Create a REST API endpoint for user authentication with proper error handling, tests, and documentation
```

This will demonstrate:
1. Prompt analysis and requirement extraction
2. Multi-agent coordination
3. Full development workflow

### 3. Code Modification Request

Test code modification capabilities:
```
Update the factorial function to include input validation and error handling
```

This shows:
1. Context understanding
2. Existing code analysis
3. Modification planning

### 4. Testing and Documentation Focus

Request focused on tests:
```
Create unit tests for the user authentication endpoint
```

Observe:
1. Test requirement analysis
2. Test case generation
3. Integration with existing code

### 5. Review and Improvement

Try a review request:
```
Review the authentication implementation for security best practices
```

This demonstrates:
1. Analysis of review requirements
2. Security consideration extraction
3. Review process coordination

## Debugging and Monitoring

1. Check Debug Panel:
- Open Command Palette (Ctrl/Cmd + Shift + P)
- Type "Show Debug Panel"
- Monitor agent interactions and task flow

2. Check Debug Console:
- Open VS Code's Debug Console
- Monitor backend server logs
- Check agent communication

3. Monitor File Changes:
- Watch workspace for file modifications
- Verify generated/updated files
- Check documentation updates

## Expected Output Format

For each task, you should see structured output like:

```json
{
  "type": "agent_response",
  "status": "success",
  "prompt_analysis": {
    "enhanced_prompt": {
      "technical_requirements": [...],
      "target_agents": [...],
      "constraints": [...],
      "context": {...}
    },
    "context": {...}
  },
  "result": {
    "implementation": {...},
    "tests": {...},
    "documentation": {...},
    "review": {...}
  }
}
```

## Troubleshooting

### Common Issues

1. Connection Error:
```
Check if backend server is running on correct port
Verify WebSocket connection in VS Code console
```

2. Agent Communication Error:
```
Check .env configuration
Verify OPENAI_API_KEY is valid
Monitor debug console for specific errors
```

3. File Operation Error:
```
Check workspace path configuration
Verify file permissions
Monitor file operation logs
```

### Debug Logs

Enable detailed logging:
1. Set `verbose: true` in agents.yaml
2. Monitor `src/backend/debug/logs` directory
3. Check VS Code Output panel with "Agenta" selected

## Performance Monitoring

Monitor system performance:
1. Task processing time
2. Agent communication overhead
3. Memory usage
4. API rate limits

## Example Test Suite

Create a file `test_suite.py`:

```python
import asyncio
from backend.main import Backend

async def test_prompt_engineering():
    backend = Backend()
    
    # Test cases
    test_requests = [
        "Create a simple calculator function",
        "Add unit tests for the calculator",
        "Document the calculator implementation",
        "Review the calculator code"
    ]
    
    for request in test_requests:
        result = await backend.message_handler.handle_message({
            'type': 'task',
            'content': request,
            'correlation_id': 'test-123'
        })
        
        # Verify prompt analysis
        assert 'prompt_analysis' in result
        assert 'enhanced_prompt' in result['prompt_analysis']
        
        # Verify task execution
        assert result['status'] == 'success'
        print(f"Test passed for: {request}")

if __name__ == "__main__":
    asyncio.run(test_prompt_engineering())
```

Run the test suite:
```bash
python test_suite.py
```

## Success Criteria

✅ Prompt analysis provides clear technical requirements
✅ Agent selection matches task needs
✅ Tasks are properly coordinated
✅ Results include context and explanations
✅ Error handling works effectively
✅ Performance is within acceptable range
