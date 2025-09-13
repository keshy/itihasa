<div align="center">

# Itihasa

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python Version](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/imports-isort-ef8336.svg)](https://pycqa.github.io/isort/)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/keshy/itihasa/ci.yml?branch=main&label=CI/CD&logo=github-actions&logoColor=white)](https://github.com/keshy/itihasa/actions/workflows/ci.yml)
[![Last Commit](https://img.shields.io/github/last-commit/keshy/itihasa?logo=github)](https://github.com/keshy/itihasa/commits/main)
[![Open Issues](https://img.shields.io/github/issues-raw/keshy/itihasa?color=red&logo=github)](https://github.com/keshy/itihasa/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://makeapullrequest.com)

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
git clone https://github.com/keshy/itihasa.git
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
