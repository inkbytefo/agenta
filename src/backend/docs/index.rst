CrewAI VSCode Extension Documentation
==================================

Welcome to the CrewAI VSCode Extension documentation. This documentation covers the backend implementation of the agent-based code assistance system.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   introduction
   installation
   architecture
   api/index
   development
   testing

Introduction
-----------

The CrewAI VSCode Extension is a powerful tool that integrates AI-powered agents into your development workflow. It provides intelligent code assistance, documentation generation, and code review capabilities.

Quick Start
----------

.. code-block:: bash

   # Install Python dependencies
   pip install -r src/backend/requirements.txt

   # Configure environment
   cp src/backend/.env.template src/backend/.env
   # Edit .env with your API keys and settings

   # Start the extension in development mode
   code . && F5

Architecture Overview
------------------

The extension is built on a multi-agent system using the CrewAI framework:

* Base Agent System
* Specialized Agents (Code, Documentation, Review, etc.)
* Task Management
* Memory Management
* IPC Communication

API Reference
------------

.. toctree::
   :maxdepth: 2
   :caption: API Documentation:

   api/agents/index
   api/utils/index
   api/memory/index
   api/ipc/index
   api/tools/index

Agents
~~~~~~

.. autosummary::
   :toctree: api/agents
   
   agents.base_agent.VSCodeAgent
   agents.code_agent.CodeAgent
   agents.documentation_agent.DocumentationAgent
   agents.review_agent.ReviewAgent
   agents.test_agent.TestAgent

Utilities
~~~~~~~~

.. autosummary::
   :toctree: api/utils
   
   agents.utils.task_utils.TaskType
   agents.utils.task_utils.TaskDetector
   agents.utils.task_utils.TaskFormatter
   agents.utils.task_utils.TaskTemplateManager
   agents.utils.task_utils.ResponseFormatter

Memory Management
~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: api/memory
   
   memory.memory_manager.MemoryManager

IPC Communication
~~~~~~~~~~~~~~

.. autosummary::
   :toctree: api/ipc
   
   ipc.message_handler.MessageHandler

Development Guide
---------------

Contributing
~~~~~~~~~~

1. Fork the repository
2. Create a feature branch
3. Follow coding standards (see DeveloperGuide.MD)
4. Add tests
5. Submit PR

Testing
-------

Running Tests
~~~~~~~~~~

.. code-block:: bash

   # Run all tests
   pytest src/backend/tests

   # Run specific test file
   pytest src/backend/tests/test_code_agent.py

   # Run with coverage
   pytest --cov=src/backend src/backend/tests

Code Coverage
~~~~~~~~~~

.. code-block:: bash

   # Generate coverage report
   pytest --cov=src/backend --cov-report=html src/backend/tests

Security
-------

Security Considerations
~~~~~~~~~~~~~~~~~~~

* API key management through environment variables
* Input validation and sanitization
* Rate limiting and abuse prevention
* Secure IPC communication

Configuration
------------

Environment Variables
~~~~~~~~~~~~~~~~~~

See ``.env.template`` for all available configuration options:

* LLM Provider settings
* API keys and endpoints
* Memory and cache settings
* Debug options

Agent Configuration
~~~~~~~~~~~~~~~~

Agents are configured through ``src/backend/config/agents.yaml``:

* Roles and goals
* Model preferences
* Tool access
* Memory settings

Troubleshooting
-------------

Common Issues
~~~~~~~~~~~

1. API Key Issues
   * Check .env file
   * Verify environment variables

2. IPC Communication
   * Check port availability
   * Verify WebSocket connection

3. Memory Management
   * Check file permissions
   * Verify cache directory exists

Logging
~~~~~~

* Logs are stored in ``logs/`` directory
* Set LOG_LEVEL in .env for desired verbosity

Indices and Tables
----------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`