# Vampire Chat 🦇

A delightful chat application featuring Lilly, your friendly teenage vampire AI companion. Built with Python, OpenAI's GPT-4, and Gradio.

## Features

- 💬 Natural conversation with a vampire-themed AI personality
- 🎤 Voice input support with speech-to-text conversion
- 🧠 Context-aware responses using conversation history
- 🎨 Beautiful, vampire-themed user interface
- 🔍 Semantic search for relevant conversation context

## Installation

### From PyPI (Coming Soon)
```bash
pip install vampire-chat
```

### From Source
```bash
git clone https://github.com/yourusername/vampire-chat
cd vampire-chat
pip install -e ".[dev]"  # Install with development dependencies
```

## Quick Start

1. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

2. Run the application:
```bash
vampire-chat
```

Or run directly with Python:
```bash
python runVampire.py
```

## Development Setup

1. Install development dependencies:
```bash
pip install -e ".[dev]"
```

2. Set up pre-commit hooks:
```bash
pre-commit install
```

3. Run tests:
```bash
pytest
```

## Project Structure

```
vampire-chat/
├── vampire_chat/          # Main package directory
│   ├── app/              # Application code
│   ├── database/         # Database management
│   └── utils/            # Utility functions
├── tests/                # Test files
├── docs/                 # Documentation
├── setup.py             # Package configuration
├── requirements.txt     # Production dependencies
└── README.md           # This file
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for the GPT-4 API
- Gradio team for the wonderful UI framework
- All contributors and users of this project 