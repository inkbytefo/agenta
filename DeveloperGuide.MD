# CrewAI VSCode Extension Developer Guide

## 📋 Table of Contents
- [Development Setup](#-development-setup)
- [Code Standards](#-code-standards)
- [Architecture](#-architecture)
- [Security Guidelines](#-security-guidelines)
- [Testing Standards](#-testing-standards)
- [Communication Protocol](#-communication-protocol)
- [Contributing](#-contributing)

## 🛠 Development Setup

### Prerequisites
- Node.js v18+
- Python 3.9+
- VSCode 1.85+
- Git

### Installation Steps
```bash
# 1. Create extension skeleton
npm install -g yo generator-code
yo code

# 2. Install Python dependencies
pip install -r src/backend/requirements.txt

# 3. Start in development mode
code . && F5
```

## 📝 Code Standards

### TypeScript Standards
- Use ESLint with the following configuration:
```json
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:prettier/recommended"
  ],
  "rules": {
    "@typescript-eslint/explicit-function-return-type": "error",
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/no-unused-vars": "error",
    "no-console": ["warn", { "allow": ["warn", "error"] }]
  }
}
```

### Python Standards
- Follow PEP 8 guidelines
- Use pylint with the following configuration:
```ini
[MASTER]
disable=
    C0111, # missing-docstring
    C0103, # invalid-name
    R0903, # too-few-public-methods

[FORMAT]
max-line-length=100

[MESSAGES CONTROL]
disable=broad-except,logging-fstring-interpolation
```

### Code Formatting
- TypeScript: Use Prettier
- Python: Use Black with line length 100
```bash
# Format TypeScript
npm run format

# Format Python
black src/backend --line-length 100
```

### Naming Conventions
- TypeScript:
  - Interfaces: PascalCase with 'I' prefix (e.g., IAgentConfig)
  - Types: PascalCase (e.g., AgentResponse)
  - Variables/Functions: camelCase
  - Constants: UPPER_SNAKE_CASE

- Python:
  - Classes: PascalCase
  - Functions/Variables: snake_case
  - Constants: UPPER_SNAKE_CASE
  - Private members: Prefix with underscore

### Code Organization
```
src/
├── backend/                 # Python backend
│   ├── agents/             # Agent implementations
│   ├── memory/             # Memory management
│   ├── tools/              # Agent tools
│   ├── ipc/                # Inter-process communication
│   └── config/             # Configuration files
│
└── extension/              # VSCode extension
    ├── webview/           # Frontend implementation
    ├── utils/             # Utility functions
    └── types/             # TypeScript type definitions
```

### Import Order
- Python:
```python
# Standard library imports
import os
import json

# Third-party imports
import crewai
from langchain import tools

# Local application imports
from .agents import BaseAgent
from .config import settings
```

- TypeScript:
```typescript
// Node built-in modules
import * as path from 'path';

// Third-party imports
import * as vscode from 'vscode';

// Local imports
import { AgentConfig } from './types';
```

## 🔒 Security Guidelines

### API Key Management
- Never store API keys in code
- Use environment variables for sensitive data
- Implement key rotation mechanism
- Use VSCode's Secret Storage API for client-side storage

### Input Validation
- Sanitize all user inputs
- Validate file paths
- Implement strict type checking
- Use parameterized queries

### Error Handling
```typescript
try {
  await performOperation();
} catch (error) {
  if (error instanceof OperationError) {
    vscode.window.showErrorMessage(`Operation failed: ${error.message}`);
  } else {
    // Log unexpected errors
    console.error('Unexpected error:', error);
    vscode.window.showErrorMessage('An unexpected error occurred');
  }
}
```

## 🧪 Testing Standards

### Unit Tests
- Python: pytest
- TypeScript: Jest
- Minimum 80% code coverage
- Test structure:
```typescript
describe('ComponentName', () => {
  describe('methodName', () => {
    it('should handle successful case', async () => {
      // Arrange
      // Act
      // Assert
    });

    it('should handle error case', async () => {
      // Test error scenarios
    });
  });
});
```

### Integration Tests
- Test IPC communication
- Test file system operations
- Test API integrations
- Use mocks for external services

### E2E Tests
- Test complete user workflows
- Use VSCode Extension Testing API
- Simulate user interactions

## 🔄 Git Workflow

### Branch Naming
- feature/feature-name
- bugfix/bug-description
- hotfix/critical-fix
- release/version-number

### Commit Messages
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Adding tests
- chore: Maintenance

### Pull Request Process
1. Create feature branch
2. Write/update tests
3. Update documentation
4. Submit PR with description
5. Pass CI checks
6. Get code review
7. Merge after approval

## 📡 Communication Protocol

### Message Format
```typescript
interface BaseMessage {
  type: MessageType;
  timestamp: number;
  correlationId: string;
  payload: unknown;
}

enum MessageType {
  TASK = 'task',
  RESPONSE = 'response',
  ERROR = 'error',
  STATUS = 'status'
}
```

## 🤝 Contributing

### Getting Started
1. Fork the repository
2. Create feature branch
3. Install dependencies
4. Make changes
5. Run tests
6. Submit PR

### Code Review Process
- All code must be reviewed
- Automated checks must pass
- Documentation must be updated
- Tests must be included
- Follow style guide

### Documentation
- Update README.md for user-facing changes
- Update DeveloperGuide.MD for developer changes
- Include JSDoc/docstring comments
- Keep architecture diagrams updated

## 📚 Additional Resources
- [VSCode Extension API](https://code.visualstudio.com/api)
- [CrewAI Documentation](https://www.crewai.com/docs)
- [TypeScript Guidelines](https://www.typescriptlang.org/docs/handbook/intro.html)
- [Python Style Guide](https://www.python.org/dev/peps/pep-0008/)

## License
MIT License - See [LICENSE](LICENSE) for details
