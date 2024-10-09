# reverse-engineering 🧠💻

![Project Logo](https://github.com/user-attachments/assets/10f2da63-9893-46d5-a7b9-d138c834f5ac)

> Unleash the power of AI to dissect, analyze, and transform your code.

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

**reverse-engineering** is a revolutionary AI-powered command-line tool designed to help developers, engineers, researchers, and students interact with source code like never before. By leveraging cutting-edge Large Language Models (LLMs), it brings capabilities such as code analysis, refactoring suggestions, and security audits directly to your development environment, transforming the way you approach software development.

Whether you're working with an old, undocumented codebase, optimizing software performance, or learning new coding paradigms, **reverse-engineering** is your trusted AI companion in the software engineering journey.

---

## Table of Contents
- [Features](#features)
- [Motivation](#motivation)
- [Installation](#installation)
- [Configuration](#configuration)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
- [How It Works](#how-it-works)
- [Terminal Commands for cli.py](#terminal-commands-for-clipy)
- [Architecture Overview](#architecture-overview)
- [Extending reverse-engineering](#extending-reverse-engineering)
- [Dependencies](#dependencies)
- [Best Practices](#best-practices)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [Community](#community)
- [License](#license)
- [Acknowledgments](#acknowledgments)
- [Citation](#citation)

## Features

- **🔍 Deep Code Analysis**: Uncover the intricacies of any codebase with AI-powered insights, including code structure, complexity, and logic flow.
- **📊 Static Code Analysis**: Perform thorough static code analysis during the code review process.
- **🔄 Refactoring Suggestions**: Provide intelligent refactoring suggestions powered by static analysis for enhanced code quality.
- **✏️ Code Snippet Auto-Generation**: Automatically generate useful code snippets to accelerate development.
- **🌐 Internet Requirement Note**: The tool currently requires an active internet connection to support analysis and refactoring features.
- **🐞 Intelligent Bug Detection**: Automatically identify potential issues in your code, from syntax errors to logical vulnerabilities.
- **🚀 Performance Optimization**: Get tailored suggestions to boost your code's efficiency, covering best practices in data structures, algorithms, and design patterns.
- **📚 Automatic Documentation**: Generate comprehensive, human-readable documentation with a single command, saving valuable time in explaining the "what" and "why" of your code.
- **🔄 Smart Refactoring**: Suggest restructuring and improvements to make the code cleaner and more maintainable, while preserving its core functionality.
- **🧪 Test Case Generation**: Create robust test suites based on the existing codebase, covering edge cases and ensuring higher reliability.
- **🔒 Security Auditing**: Detect vulnerabilities and receive AI-generated mitigation strategies to safeguard your application.
- **🌐 Multi-Language Support**: Seamless support for multiple programming languages, including Python, Java, C++, JavaScript, Ruby, Rust, and more.
- **🧠 Algorithm Explanation**: Demystify complex algorithms with clear, concise explanations, perfect for educational purposes.
- **🔄 Code Translation**: Seamlessly convert code between different programming languages—ideal for migrating legacy systems or adapting software for new environments.

## Motivation

In today's fast-paced software development world, code understanding and maintenance are more critical than ever. Legacy systems, large codebases, security concerns, and constant technological evolution create significant challenges for developers. This project was born to address key pain points:

1. **Reducing Time and Complexity**: Understanding a new or legacy codebase can take weeks. **reverse-engineering** aims to reduce this time by up to 60%, making onboarding and code review more efficient.
2. **AI-Powered Insights for Quality and Security**: Most code editors and IDEs only offer syntactic checks. Our tool integrates LLMs to provide semantic analysis, detecting logical errors and security vulnerabilities that typical static analysis tools may miss.
3. **Facilitating Learning**: Understanding and replicating advanced algorithms and design patterns can be challenging for students and junior developers. **reverse-engineering** acts as a learning assistant, explaining each component clearly and succinctly.

## Installation

### Requirements

- Python 3.7+
- Git
- [Conda](https://docs.conda.io/en/latest/miniconda.html) or [Poetry](https://python-poetry.org/docs/#installation) (optional, but recommended for dependency management)
- [Docker](https://www.docker.com/get-started) (optional, for containerized usage)

### Installation Options

1. **Using conda**:

   ```bash
   # Clone the repository
   git clone https://github.com/JacquesGariepy/reverse-engineering.git
   cd reverse-engineering

   # Create and activate a new conda environment
   conda create -n reverse-engineer python=3.9
   conda activate reverse-engineer

   # Install dependencies
   conda install -c conda-forge typer pydantic python-dotenv pyyaml requests
   pip install aider
   ```

2. **Using poetry**:

   ```bash
   # Clone the repository
   git clone https://github.com/JacquesGariepy/reverse-engineering.git
   cd reverse-engineering

   # Install dependencies using poetry
   poetry install
   ```

3. **Using pip**:

   ```bash
   # Clone the repository
   git clone https://github.com/JacquesGariepy/reverse-engineering.git
   cd reverse-engineering

   # Install dependencies
   pip install -r requirements.txt
   ```

4. **Using Docker**:

   You can also run **reverse-engineering** using Docker, which ensures a consistent environment across different platforms.

   ```bash
   # Clone the repository
   git clone https://github.com/JacquesGariepy/reverse-engineering.git
   cd reverse-engineering

   # Build Docker image for Linux
   docker build -f Dockerfile.linux -t reverse-engineering:linux .

   # Run Docker container
   docker run -it --rm -v $(pwd):/app reverse-engineering:linux
   ```

## Configuration

1. Create a `.env` file in the project root directory with your API keys:
   ```dotenv
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```
2. Create a `config.yaml` file with the model configurations:
   ```yaml
   default_model: "gpt-4o-2024-08-06"
   models:
     gpt-4o-2024-08-06:
       name: "gpt-4o-2024-08-06"
       provider: "openai"
       max_tokens: 128000
       temperature: 0.7
     claude-3-5-sonnet-20240620:
       name: "claude-3-5-sonnet-20240620"
       provider: "anthropic"
       max_tokens: 200000
       temperature: 0.7

   rate_limit:
     limit: 150000
     time_frame: 300
   ```

## Quick Start

After installation and configuration, you can start using **reverse-engineering** right away:

```bash
# Initialize the tool
python .\reverseEngineer\cli.py init

# Analyze a Python file
analyze --file "C:\Temp\test\mycode.py" --language python --test-file "test_mycode.py"

# Refactoring
refactor --file "C:\Temp\test\mycode.py" --language python --test-file "test_mycode.py"

# Generate documentation for a JavaScript file
python cli.py generate-documentation --file path/to/your/code.js --language javascript

# Perform a security audit on a C++ file
python cli.py security-audit --file path/to/your/code.cpp --language cpp
```

## Usage Examples

### Code Analysis

```bash
python cli.py analyze --file complex_algorithm.py --language python
```

**Example Output**:
```
Analysis of complex_algorithm.py:
1. The file implements a graph traversal algorithm using depth-first search.
2. Key functions:
   - create_graph(): Initializes the graph structure
   - dfs(graph, start, visited=None): Performs the depth-first search
3. Time complexity: O(V + E), where V is the number of vertices and E is the number of edges.
4. Space complexity: O(V) for the visited set and recursion stack.
5. Potential optimization: Consider using an iterative approach to reduce stack overflow risk for large graphs.
```

### Security Audit

```bash
python cli.py security-audit --file login_system.php --language php
```

**Example Output**:
```
Security Audit Results for login_system.php:
1. [HIGH] SQL Injection vulnerability detected on line 23. Use prepared statements instead of string concatenation.
2. [MEDIUM] Weak password hashing algorithm (MD5) used. Recommend switching to bcrypt or Argon2.
3. [LOW] Session ID is not regenerated after login, potentially allowing session fixation attacks.
4. [INFO] Consider implementing rate limiting to prevent brute force attacks.
```

## Terminal Commands for cli.py

```bash
# Initialize the ReverseEngineer tool with default config
python cli.py init

# Analyze a code file
python cli.py analyze --file path/to/file.py --language python --output analysis_result.txt

# Identify issues in the code
python cli.py identify-issues --file path/to/file.js --language javascript --output issues_report.txt

# Suggest optimizations
python cli.py optimize --file path/to/script.py --language python --output optimizations.txt

# Generate documentation
python cli.py generate-documentation --file path/to/main.cpp --language cpp --output documentation.md

# Suggest refactoring improvements
python cli.py refactor --file path/to/app.rb --language ruby --output refactoring_suggestions.txt

# Explain algorithm
python cli.py explain-algorithm --file path/to/algo.py --language python --output algorithm_explanation.txt

# Generate test cases
python cli.py generate-test-cases --file path/to/module.py --language python --output test_cases.py

# Identify design patterns
python cli.py identify-design-patterns --file path/to/system.cpp --language cpp --output patterns_used.txt

# Convert the code language
python cli.py convert-language --file path/to/script.py --from-language python --to-language javascript --output converted.js

# Perform a security audit
python cli.py security-audit --file path/to/webapp.js --language javascript --output security_report.txt

# Interactive mode
python cli.py
```

## Architecture Overview

**reverse-engineering** relies on several core components:

- **Command Line Interface**: Powered by `Typer`, the CLI acts as the gateway to interacting with the tool's core capabilities.
- **ReverseEngineer Core**: The main logic, including language model interaction, is handled by the `ReverseEngineer` class.
- **Utilities Module**: Handles auxiliary functions, such as file reading, processing commands, and saving outputs.
- **Language Models**: Supports OpenAI's GPT, Anthropic's Claude, and other LLMs, depending on user preferences and configurations.
- **Interactive Shell**: After executing a command, users can continue in an interactive mode, allowing iterative analysis without restarting the tool.

## How It Works

**reverse-engineering** uses the `aider` library to interact with different language models. It loads configurations from YAML files and environment variables, initializes the models, and uses `typer` to expose the core functionality via CLI. This combination ensures that:

1. Developers can easily switch between different models.
2. The output can be customized and tailored to user requirements.
3. It can scale from individual analysis to integrating it into CI/CD workflows.

## Dependencies

- [typer](https://typer.tiangolo.com/): For creating the command-line interface.
- [pydantic](https://pydantic-docs.helpmanual.io/): For data validation and settings management.
- [python-dotenv](https://github.com/theskumar/python-dotenv): For loading environment variables.
- [PyYAML](https://pyyaml.org/): For parsing YAML configuration files.
- [requests](https://docs.python-requests.org/en/master/): For making HTTP requests.
- [aider](https://github.com/paul-gauthier/aider): For interacting with language models.

## Best Practices

- **Keep Configuration Files Up to Date**: Maintain `.env` and `config.yaml` for the latest API keys and model settings.
- **Integrate Security Audits**: Perform regular security audits on new commits to maintain codebase integrity.
- **Refactor Regularly**: Use the smart refactoring feature periodically to improve code quality and reduce technical debt.

## Contributing

We welcome contributions from the community! Whether it's adding new features, improving documentation, or reporting bugs, your input is valuable. Please check out our [Contribution Guidelines](CONTRIBUTING.md) for more information on how to get started.

## Roadmap

We're continuously working to improve **reverse-engineering**. Here's what we have planned for the future:

- **Integration with Popular IDEs** (VSCode, PyCharm).
- **Support for More Programming Languages**: Including TypeScript, Swift, Kotlin, etc.
- **Enhanced Visualization** of code analysis results.
- **API Endpoint for Integration with CI/CD Pipelines**.
- **Collaborative Code Analysis Features**: Real-time code analysis across distributed teams.

## Community

Join our community to discuss **reverse-engineering**, share your experiences, and get help:

- [Discord Server](https://discord.gg/reverse-engineering)
- [Reddit Community](https://www.reddit.com/r/reverse-engineeringAI)
- [Twitter](https://twitter.com/reverse-engineeringAI)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- The `aider` library for providing an easy way to interact with language models.
- The open-source community for the various libraries used in this project.

## Citation

If you use **reverse-engineering** in your research or project, please cite it as follows:

```
@software{reverse-engineering,
  author = {Jacques Gariépy},
  title = {reverse-engineering: A LLM-powered tool for code analysis and manipulation},
  year = {2024},
  url = {https://github.com/JacquesGariepy/reverse-engineering}
}
```

---

<p align="center">
  Made with ❤️ by the reverse-engineering Team
</p>

<p align="center">
  <a href="#top">Back to Top</a>
</p>
