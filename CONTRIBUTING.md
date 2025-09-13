# Contributing to Itihasa

Thank you for your interest in contributing to Itihasa! This document provides guidelines and information for contributors.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and constructive in all interactions.

## How to Contribute

### Reporting Issues

1. Check existing issues to avoid duplicates
2. Use the issue template when available
3. Provide detailed information:
   - Operating system and version
   - Python version
   - Steps to reproduce the issue
   - Expected vs actual behavior
   - Error messages or logs

### Suggesting Features

1. Open an issue with the "enhancement" label
2. Describe the feature and its use case
3. Explain why it would be valuable to the project
4. Consider implementation complexity and maintenance burden

### Contributing Code

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/itihasa.git
   cd itihasa
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install pytest black flake8 isort
   ```

4. **Make your changes**
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed
   - Ensure all tests pass

5. **Run quality checks**
   ```bash
   # Format code
   black src/
   isort src/
   
   # Lint code
   flake8 src/
   
   # Run tests
   pytest tests/
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

7. **Push and create a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Development Guidelines

### Code Style

- Follow PEP 8 guidelines
- Use Black for code formatting
- Use isort for import sorting
- Maximum line length: 127 characters
- Use meaningful variable and function names

### Testing

- Write tests for new functionality
- Maintain or improve test coverage
- Use descriptive test names
- Test both success and failure cases

### Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions and classes
- Update CHANGELOG.md following Keep a Changelog format
- Include code examples where helpful

### Commit Messages

Use clear, descriptive commit messages:
- Start with a verb in present tense
- Keep the first line under 50 characters
- Add detailed description if needed

Examples:
```
Add support for Marathi language translation
Fix audio generation timeout issue
Update documentation for new API endpoints
```

## Project Structure

```
itihasa/
├── src/                    # Source code
│   ├── config/            # Configuration handling
│   ├── content/           # Content processing
│   ├── manager/           # Management utilities
│   ├── publisher/         # Publishing tools
│   ├── utils/             # Utility functions
│   ├── worker/            # Background workers
│   ├── main.py            # Core translation logic
│   └── generate.py        # Content generation
├── tests/                 # Test suite
├── data/                  # Sample data and datasets
├── .github/workflows/     # CI/CD configuration
└── docs/                  # Additional documentation
```

## Setting Up Google Cloud

For development involving Google Cloud services:

1. Create a Google Cloud Project
2. Enable required APIs:
   - Vertex AI API
   - Text-to-Speech API
3. Create a service account with appropriate permissions
4. Download the service account key
5. Set environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
   ```

## Pull Request Process

1. Ensure your PR has a clear title and description
2. Reference any related issues
3. Include screenshots for UI changes
4. Ensure all CI checks pass
5. Request review from maintainers
6. Address feedback promptly

## Release Process

Releases follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

## Getting Help

- Check existing documentation
- Search through issues
- Join our community discussions
- Contact maintainers for complex questions

## Recognition

Contributors will be recognized in:
- CHANGELOG.md for significant contributions
- README.md contributors section
- Release notes for major features

Thank you for contributing to Itihasa! 🙏
