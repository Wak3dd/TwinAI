# TwinAI

**TwinAI** is a desktop application for orchestrating dialogues between two AI models. Built with CustomTkinter, it provides a polished interface for configuring, monitoring, and managing conversations between different LLM providers with full streaming support.

## Features

- **Dual AI Dialogue**: Configure two independent bots and watch them converse in an automatic cycle or manually guide the conversation.
- **Multi-Provider Support**: Native integration with OpenAI, Anthropic, Mistral, and Ollama.
- **Custom Provider**: Connect to any OpenAI-compatible or Anthropic-compatible API (vLLM, LocalAI, LiteLLM, etc.).
- **Secure Storage**: API keys are encrypted at rest using Fernet symmetric encryption (`cryptography` library).
- **Chat Management**: Create, switch, delete, export, and import multiple chat sessions.
- **Streaming Responses**: Real-time token-by-token response rendering.
- **Message Control**: Edit messages, delete message pairs (request + response), or write manually as either bot.
- **Advanced Bot Configuration**: System prompts, tone, emoji frequency, temperature, max tokens, and forced response language.
- **Localization**: Full UI translation support (English, Russian).
- **Theming**: Dark/Light mode with customizable font family and size.

## Installation

### Prerequisites

- Python 3.9+
- pip

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/twinai.git
   cd twinai
