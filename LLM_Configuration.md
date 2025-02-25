# LLM Provider Configuration Guide

## Overview
This guide explains how to configure and use different Language Model (LLM) providers in the Agenta system. Each agent can be configured to use a specific LLM provider and model.

## Supported Providers

1. **OpenAI**
   - Models: GPT-4, GPT-4 Turbo, GPT-3.5 Turbo
   - Configuration required: `OPENAI_API_KEY`

2. **Google AI**
   - Models: Gemini Pro, Gemini Pro Vision
   - Configuration required: 
     ```
     GOOGLE_API_KEY
     GOOGLE_PROJECT_ID (for VertexAI)
     GOOGLE_LOCATION (for VertexAI)
     ```

3. **Anthropic**
   - Models: Claude-3 Opus, Claude-3 Sonnet, Claude-2.1
   - Configuration required: `ANTHROPIC_API_KEY`

4. **OpenRouter**
   - Multiple models from different providers
   - Configuration required: `OPENROUTER_API_KEY`
   - Provides access to:
     - OpenAI models
     - Anthropic models
     - Meta's Llama models
     - Mistral models
     - DeepSeek models

## Configuration Methods

### 1. Using the UI

1. Open the LLM Settings panel:
   - Click the gear icon in the status bar, or
   - Use Command Palette: "Configure LLM Providers"

2. For each agent, you can configure:
   - Provider selection
   - Model selection
   - API key
   - Temperature
   - Max tokens
   - Additional settings

### 2. Using Environment Variables

1. Copy `.env.template` to `.env`:
   ```bash
   cp src/backend/.env.template src/backend/.env
   ```

2. Set your API keys and default configurations:
   ```env
   OPENAI_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_key_here
   GOOGLE_API_KEY=your_key_here
   ```

3. Configure agent-specific settings:
   ```env
   CODE_AGENT_MODEL=gpt-4
   TEST_AGENT_MODEL=claude-2
   DOCUMENTATION_AGENT_MODEL=gemini-pro
   ```

### 3. Using YAML Configuration

Edit `src/backend/config/agents.yaml`:

```yaml
code_agent:
  llm:
    provider: openai
    model: gpt-4
    temperature: 0.7
    max_tokens: 2000

test_agent:
  llm:
    provider: anthropic
    model: claude-3-sonnet
    temperature: 0.6
```

## Provider-Specific Settings

### OpenAI
```yaml
provider: openai
model: gpt-4
temperature: 0.7
max_tokens: 2000
additional_config:
  top_p: 1.0
  presence_penalty: 0
  frequency_penalty: 0
```

### Google AI (Gemini)
```yaml
provider: gemini
model: gemini-pro
temperature: 0.7
max_tokens: 2048
additional_config:
  top_k: 40
  top_p: 0.95
```

### Anthropic
```yaml
provider: anthropic
model: claude-3-opus
temperature: 0.7
max_tokens: 4000
additional_config:
  top_k: 50
```

### OpenRouter
```yaml
provider: openrouter
model: openai/gpt-4-turbo
temperature: 0.7
max_tokens: 2000
additional_config:
  route_prefix: your_prefix  # Optional
```

## Default Settings

Each agent type has recommended default settings:

1. **Prompt Engineer Agent**
   - Default: GPT-4 
   - Temperature: 0.9 (more creative)
   - Higher token limit for complex prompt analysis

2. **Code Agent**
   - Default: GPT-4 or Claude-3
   - Temperature: 0.7
   - Focus on code accuracy

3. **Test Agent**
   - Default: GPT-3.5 Turbo or Gemini Pro
   - Temperature: 0.6
   - Focus on test coverage

4. **Documentation Agent**
   - Default: GPT-3.5 Turbo or Claude-2
   - Temperature: 0.6
   - Clear and consistent documentation

5. **Review Agent**
   - Default: GPT-4 or Claude-3
   - Temperature: 0.7
   - Thorough code review

## Best Practices

1. **API Key Security**
   - Never commit API keys to version control
   - Use environment variables for sensitive data
   - Rotate API keys regularly

2. **Cost Optimization**
   - Use cheaper models for simpler tasks
   - Configure appropriate max_tokens
   - Enable caching for repeated operations

3. **Performance Tuning**
   - Adjust temperature based on task needs
   - Configure rate limits appropriately
   - Monitor and optimize token usage

4. **Error Handling**
   - Set up fallback providers
   - Configure retry mechanisms
   - Monitor API rate limits

## Troubleshooting

### Common Issues

1. **API Key Issues**
   - Verify key is correctly set
   - Check key permissions
   - Verify billing status

2. **Rate Limiting**
   - Check `MAX_REQUESTS_PER_MINUTE`
   - Verify account limits
   - Monitor usage patterns

3. **Model Availability**
   - Verify model access rights
   - Check provider status
   - Confirm model deployment region

### Getting Help

1. Check the debug console for detailed error messages
2. Review provider documentation
3. Check system logs in `.crewai_memories`
4. Verify network connectivity
5. Check provider status pages

## Monitoring and Maintenance

1. **Usage Monitoring**
   - Track token usage
   - Monitor response times
   - Check error rates

2. **Regular Updates**
   - Update provider configurations
   - Check for new models
   - Update API versions

3. **Performance Optimization**
   - Review caching effectiveness
   - Optimize prompt templates
   - Adjust model parameters

## Advanced Configuration

### Custom Providers

Add custom providers by:
1. Creating provider class
2. Implementing required interfaces
3. Registering in provider manager
4. Adding configuration options

### Fallback Configuration

Configure fallback providers:
```yaml
fallback_config:
  providers:
    - openai
    - anthropic
    - gemini
  retry_attempts: 3
  timeout: 30
```

### Load Balancing

Configure multiple providers:
```yaml
load_balancing:
  enabled: true
  strategy: round_robin
  weights:
    openai: 0.6
    anthropic: 0.4
