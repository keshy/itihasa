<div align="center">

# Itihasa

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/imports-isort-ef8336.svg)](https://pycqa.github.io/isort/)
[![Codecov](https://img.shields.io/codecov/c/github/yourusername/itihasa/main?logo=codecov&logoColor=white)](https://codecov.io/gh/yourusername/itihasa)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/yourusername/itihasa/ci.yml?branch=main&label=CI/CD&logo=github-actions&logoColor=white)](https://github.com/yourusername/itihasa/actions/workflows/ci.yml)
[![Documentation Status](https://readthedocs.org/projects/itihasa/badge/?version=latest)](https://itihasa.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/itihasa.svg)](https://pypi.org/project/itihasa/)
[![CodeFactor](https://www.codefactor.io/repository/github/yourusername/itihasa/badge)](https://www.codefactor.io/repository/github/yourusername/itihasa)
[![Maintainability](https://api.codeclimate.com/v1/badges/your-code-climate-id/maintainability)](https://codeclimate.com/github/yourusername/itihasa/maintainability)
[![Open Issues](https://img.shields.io/github/issues-raw/yourusername/itihasa?color=red&logo=github)](https://github.com/yourusername/itihasa/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![Last Commit](https://img.shields.io/github/last-commit/yourusername/itihasa?logo=github)](https://github.com/yourusername/itihasa/commits/main)
[![Discord](https://img.shields.io/discord/your-discord-server?color=7289da&label=Chat%20on%20Discord&logo=discord&logoColor=white)](https://discord.gg/your-discord-invite)
[![Twitter Follow](https://img.shields.io/twitter/follow/yourusername?style=social)](https://twitter.com/yourusername)

</div>

A powerful AI-driven tool for processing, translating, and generating audio content from ancient Sanskrit texts like the Mahabharata. Itihasa leverages Google's Vertex AI and Text-to-Speech services to make ancient wisdom accessible across multiple languages.

## Features

- **Multi-language Translation**: Translate Sanskrit texts to English, Hindi, Tamil, Gujarati, Bengali, Kannada, and Telugu
- **AI-Powered Processing**: Uses Google's Gemini 2.0 Flash model for accurate and contextual translations
- **Text-to-Speech Generation**: Convert translated text to high-quality audio in multiple languages
- **Batch Processing**: Process large volumes of text efficiently
- **Background Processing**: Run content curation tasks in the background
- **Configurable Workflows**: Use YAML configuration files to define processing pipelines

## Prerequisites

- Python 3.7+
- Google Cloud Platform account with the following APIs enabled:
  - Vertex AI API
  - Text-to-Speech API
- Google Cloud service account with appropriate permissions
- Google Cloud Storage bucket for audio output

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/itihasa.git
cd itihasa
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up Google Cloud credentials:
   - Place your service account JSON file in the project root
   - Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
```

## Usage

### Basic Translation

Use the main processing script to translate Sanskrit text:

```python
from src.main import process

# Translate Sanskrit text to multiple languages
translations, error = process(
    text="नारायणं नमस्कृत्य नरं चैव नरॊत्तमम्",
    lang="SANSKRIT"
)

if not error:
    for lang_code, translation in translations.items():
        print(f"{lang_code}: {translation}")
```

### Content Curation

Use the content curator for batch processing:

```bash
python src/generate.py --config_path path/to/config.yaml
```

For background processing:

```bash
python src/generate.py --config_path path/to/config.yaml --background
```

## Configuration

The tool uses YAML configuration files to define processing workflows. See the `src/config/` directory for examples.

## Project Structure

```
itihasa/
├── src/                    # Source code
│   ├── config/            # Configuration modules
│   ├── content/           # Content processing
│   ├── manager/           # Management utilities
│   ├── publisher/         # Publishing tools
│   ├── utils/             # Utility functions
│   ├── worker/            # Worker processes
│   ├── main.py            # Main translation module
│   └── generate.py        # Content generation script
├── data/                  # Text data and datasets
├── content/               # Generated content
├── publish/               # Published outputs
├── requirements.txt       # Python dependencies
└── LICENSE               # License file
```

## Supported Languages

- **Source**: Sanskrit
- **Target Languages**:
  - English (en-US)
  - Hindi (hi-IN)
  - Tamil (ta-IN)
  - Gujarati (gu-IN)
  - Bengali (bn-IN)
  - Kannada (kn-IN)
  - Telugu (te-IN)

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Google Cloud Vertex AI and Text-to-Speech APIs
- Inspired by the rich tradition of Sanskrit literature
- Special thanks to the open source community

## Support

If you encounter any issues or have questions, please:
1. Check the [Issues](https://github.com/yourusername/itihasa/issues) page
2. Create a new issue if your problem isn't already reported
3. Provide detailed information about your environment and the issue

## Roadmap

- [ ] Support for additional source languages
- [ ] Enhanced audio customization options
- [ ] Web interface for easier usage
- [ ] Docker containerization
- [ ] API endpoints for integration

---

Made with ❤️ for preserving and sharing ancient wisdom
