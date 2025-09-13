# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial open source release
- README.md with comprehensive documentation
- CHANGELOG.md for tracking project changes
- GitHub Actions CI/CD pipeline for automated testing
- Support for multi-language translation from Sanskrit
- Text-to-speech generation capabilities
- Background processing support
- Configurable workflow system

### Changed
- Improved project structure for open source distribution
- Enhanced error handling and logging

### Fixed
- Various bug fixes and stability improvements

## [0.1.0] - 2024-09-13

### Added
- Core translation functionality using Google Vertex AI
- Support for 7 target languages (English, Hindi, Tamil, Gujarati, Bengali, Kannada, Telugu)
- Text-to-Speech integration with Google Cloud TTS
- Content curation and batch processing capabilities
- Configuration system for flexible workflows
- Data processing for Mahabharata and other Sanskrit texts

### Features
- **Translation Engine**: AI-powered Sanskrit to multi-language translation
- **Audio Generation**: High-quality text-to-speech in multiple Indian languages
- **Batch Processing**: Efficient handling of large text volumes
- **Background Jobs**: Non-blocking content processing
- **Configurable Pipelines**: YAML-based workflow configuration

### Technical Details
- Built with Python 3.7+
- Integrates Google Cloud Vertex AI (Gemini 2.0 Flash)
- Uses Google Cloud Text-to-Speech API
- Supports LINEAR16 audio encoding
- Implements proper error handling and status reporting

---

## Release Notes

### Version 0.1.0
This is the initial release of Itihasa, focusing on core functionality for translating and generating audio from Sanskrit texts. The system has been tested with Mahabharata content and supports production-ready workflows.

**Key Capabilities:**
- Translate Sanskrit verses with contextual accuracy
- Generate natural-sounding audio in multiple Indian languages
- Process content in batches with background job support
- Configure workflows through YAML files

**Known Limitations:**
- Currently supports only Sanskrit as source language
- Requires Google Cloud Platform setup
- Audio output limited to LINEAR16 format
- Translation limited to 10 languages per request

**Future Enhancements:**
- Additional source language support
- Enhanced audio format options
- Web interface development
- API endpoint creation
- Docker containerization
