# CrewAI Desktop Application

A desktop application version of the CrewAI VSCode extension, built with Tauri, React, and Python.

## Features

- Task execution interface with real-time status updates
- Debug console for monitoring events and logs
- LLM configuration management
- Cross-platform support (Windows, macOS, Linux)
- Secure API key storage
- Real-time connection status monitoring

## Prerequisites

- Node.js 16+
- Rust (latest stable)
- Python 3.8+
- Platform-specific build tools:
  - Windows: Microsoft Visual Studio C++ Build Tools
  - macOS: Xcode Command Line Tools
  - Linux: `build-essential` package

## Setup

1. Install dependencies:

```bash
# Install frontend dependencies
npm install

# Install Python backend dependencies
cd src/backend
pip install -r requirements.txt
cd ../..
```

2. Set up your environment:

Create a `.env` file in the `src/backend` directory:

```env
# LLM Provider API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
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

## Project Structure

```
.
├── src/                    # Frontend source code
│   ├── components/        # React components
│   ├── store/            # State management
│   ├── App.tsx          # Main application component
│   └── main.tsx         # Application entry point
├── src-tauri/            # Tauri application code
│   ├── src/             # Rust source code
│   └── tauri.conf.json  # Tauri configuration
└── src/backend/          # Python backend
    ├── main.py          # Backend entry point
    └── requirements.txt  # Python dependencies
```

## Adding New Features

### Frontend

1. Create new components in `src/components/`
2. Add new state management in `src/store/`
3. Update the UI in `App.tsx`

### Backend

1. Add new command handlers in `src-tauri/src/main.rs`
2. Implement corresponding Python functions in `src/backend/main.py`
3. Update the store to include new commands

## Troubleshooting

### Common Issues

1. Connection Problems
   - Check if the Python backend is running
   - Verify port availability
   - Check console for error messages

2. Build Errors
   - Ensure all dependencies are installed
   - Check platform-specific requirements
   - Verify Rust and Node.js versions

3. LLM Configuration
   - Verify API keys in environment variables
   - Check network connectivity
   - Confirm provider service status

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details
