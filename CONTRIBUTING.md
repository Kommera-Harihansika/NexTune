# Contributing to Bluetooth Headphones Price Prediction

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Development Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment: `source venv/bin/activate` (Unix) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`

## Project Structure

```
bluetooth-headphones-price-prediction/
├── data/                   # Data files (CSV)
├── models/                 # Trained models
├── notebooks/              # Jupyter notebooks for EDA
├── src/                    # Source code
│   ├── scrapers/          # Web scraping modules
│   ├── data/              # Data processing modules
│   ├── models/            # ML model modules
│   └── api/               # API modules
├── scripts/               # Execution scripts
├── tests/                 # Test files
└── .kiro/                 # Project specifications
```

## Coding Standards

- Follow PEP 8 style guide
- Add docstrings to all functions and classes
- Write unit tests for new features
- Keep functions focused and modular

## Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

Types: feat, fix, docs, style, refactor, test, chore

## Pull Request Process

1. Create a feature branch
2. Make your changes
3. Add tests
4. Update documentation
5. Submit PR with clear description

## Questions?

Open an issue for any questions or concerns.
