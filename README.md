# CrewAI Desktop Application

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![TypeScript](https://img.shields.io/badge/typescript-4.9+-blue.svg)

A desktop application that provides AI-powered development assistance using the CrewAI framework. It offers intelligent code generation, documentation, testing, and review capabilities through specialized AI agents.

## 🚀 Features

- **Intelligent Code Assistance**
  - Code generation and modification
  - Context-aware suggestions
  - Best practices enforcement

- **Documentation Support**
  - Automated documentation generation
  - Comment suggestions
  - API documentation

- **Testing Assistance**
  - Test case generation
  - Test coverage analysis
  - Edge case identification

- **Code Review**
  - Automated code reviews
  - Style guide enforcement
  - Security checking

## 📋 Requirements

- Python 3.9+
- Node.js 18+
- Rust (latest stable)
- Platform-specific build tools:
  - Windows: Microsoft Visual Studio C++ Build Tools
  - macOS: Xcode Command Line Tools
  - Linux: `build-essential` package

## 🛠️ Installation

1. **Install Dependencies**
```bash
# Install frontend dependencies
npm install

# Install Python backend dependencies
cd src/backend
pip install -r requirements.txt
cd ../..
```

2. **Configure Environment**

Create a `.env` file in the `src/backend` directory:

```env
# LLM Provider API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

## 🔧 Configuration

### LLM Provider Setup

1. Obtain API keys for supported providers:
   - OpenAI
   - Anthropic
   - Google AI

2. Add API keys to your `.env` file:
```env
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
```

## Development

Start the development server:

```bash
npm run tauri dev
```

This will launch:
- The Tauri application window
- The React development server
- The Python backend process

## Building

Create a production build:

```bash
npm run tauri build
```

This will generate platform-specific installers in the `src-tauri/target/release` directory.

## �� Development

### Project Structure
```
src/
├── backend/               # Python backend
│   ├── agents/           # AI agents
│   ├── config/          # Configuration
│   ├── tools/           # Agent tools
│   └── tests/           # Test suite
└── extension/            # VSCode extension
    ├── webview/         # UI components
    └── types/           # TypeScript types
```

### Running Tests

```bash
# Run backend tests
poetry run pytest

# Run extension tests
cd src/extension
npm test
```

### Building

```bash
# Build extension
cd src/extension
npm run package
```

### Code Style

The project uses:
- Black for Python formatting
- ESLint/Prettier for TypeScript
- Pre-commit hooks for quality checks

## 📚 Documentation

- [API Documentation](docs/api/index.html)
- [Architecture Guide](Architecture.md)
- [Development Guide](DeveloperGuide.MD)
- [Testing Guide](TestingGuide.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 🔒 Security

- API keys are stored securely using environment variables
- Rate limiting prevents API abuse
- Input validation and sanitization
- Regular security updates

Report security issues to security@yourproject.com

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [CrewAI](https://www.crewai.com/) for the AI framework
- VSCode Extension API team
- All contributors

## ❓ Troubleshooting

### Common Issues

1. **API Key Issues**
   - Verify .env file configuration
   - Check environment variables
   - Ensure correct permissions

2. **Extension Not Loading**
   - Check VSCode version
   - Verify dependencies
   - Check error logs

3. **Performance Issues**
   - Adjust rate limits
   - Check network connection
   - Monitor resource usage

For more help, see [troubleshooting guide](docs/troubleshooting.md).
