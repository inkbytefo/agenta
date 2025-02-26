# Testing Guide for CrewAI Desktop Application

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

1. Start the application in development mode:
```bash
npm run tauri dev
```

This will launch:
- The Tauri application window
- The React development server
- The Python backend process

## Running Tests

### Backend Tests

```bash
cd src/backend
pytest
```

### Frontend Tests

```bash
npm test
```

## Test Coverage

To generate a test coverage report:

```bash
cd src/backend
pytest --cov=. --cov-report=html
```

This will create an HTML report in the `htmlcov` directory.
