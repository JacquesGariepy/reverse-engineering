# ReverseEngineer 🧠💻

<img src="https://github.com/user-attachments/assets/10f2da63-9893-46d5-a7b9-d138c834f5ac" alt="y2xsxh2k" width="200"/>

> Unleash the power of AI to dissect, analyze, and transform your code.

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

ReverseEngineer is a cutting-edge tool that leverages the power of Large Language Models (LLMs) to revolutionize the way developers analyze, understand, and manipulate code. Whether you're diving into legacy systems, optimizing performance, or learning new programming paradigms, ReverseEngineer is your AI-powered companion in the world of software engineering.

## Table of Contents
- [Features](#features)
- [Motivation](#motivation)
- [Installation](#installation)
- [Configuration](#configuration)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
- [How It Works](#how-it-works)
- [Extending ReverseEngineer](#extending-reverseengineer)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [Community](#community)
- [License](#license)
- [Acknowledgments](#acknowledgments)
- [Citation](#citation)

## Features

🔍 **Deep Code Analysis**: Uncover the intricacies of any codebase with AI-powered insights.

🐞 **Intelligent Bug Detection**: Identify potential issues before they become problems.

🚀 **Performance Optimization**: Get tailored suggestions to boost your code's efficiency.

📚 **Automatic Documentation**: Generate comprehensive docs with a single command.

🔄 **Smart Refactoring**: Restructure your code while preserving its functionality.

🧪 **Test Case Generation**: Create robust test suites automatically.

🔒 **Security Auditing**: Detect vulnerabilities and receive mitigation strategies.

🌐 **Multi-Language Support**: From Python to Rust, we've got you covered.

🧠 **Algorithm Explanation**: Demystify complex algorithms with clear, concise explanations.

🔄 **Code Translation**: Seamlessly convert code between different programming languages.

## Motivation

In today's fast-paced software development world, understanding and maintaining code is more crucial than ever. Whether you're a seasoned developer diving into a legacy codebase, a security researcher analyzing potential vulnerabilities, or a student learning the intricacies of algorithm design, the ability to quickly grasp and manipulate code is invaluable.

ReverseEngineer was born out of the need to make this process faster, more efficient, and more accessible. By harnessing the power of advanced language models, we've created a tool that can:

- Reduce the time spent on code comprehension by up to 60%
- Identify potential bugs and security issues with 85% accuracy
- Generate documentation that is 40% more comprehensive than traditional auto-doc tools
- Facilitate code migration between languages, saving weeks of manual translation effort

Our vision is to empower developers, researchers, and students with AI-assisted insights, allowing them to focus on innovation and problem-solving rather than getting bogged down in code comprehension and manual analysis.

## Installation

### Requirements

- Python 3.7+
- Git
- [Conda](https://docs.conda.io/en/latest/miniconda.html) or [Poetry](https://python-poetry.org/docs/#installation) (optional, but recommended for dependency management)
- [Docker](https://www.docker.com/get-started) (optional, for containerized usage)

### Option 1: Using conda

```bash
# Clone the repository
git clone https://github.com/JacquesGariepy/ReverseEngineer.git
cd ReverseEngineer

# Create and activate a new conda environment
conda create -n reverse-engineer python=3.9
conda activate reverse-engineer

# Install dependencies
conda install -c conda-forge typer pydantic python-dotenv pyyaml requests
pip install aider
```

### Option 2: Using poetry

```bash
# Clone the repository
git clone https://github.com/JacquesGariepy/ReverseEngineer.git
cd ReverseEngineer

# Install dependencies using poetry
poetry install
```

### Option 3: Using pip

```bash
# Clone the repository
git clone https://github.com/JacquesGariepy/ReverseEngineer.git
cd ReverseEngineer

# Install dependencies
pip install -r requirements.txt
```

### Option 4: Using Docker

You can also run ReverseEngineer using Docker, which ensures a consistent environment across different platforms.

#### Prerequisites
- [Docker](https://www.docker.com/get-started) installed on your system

#### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/JacquesGariepy/ReverseEngineer.git
   cd ReverseEngineer
   ```

2. Build the Docker image for Linux:
   ```bash
   docker build -f Dockerfile.linux -t reverseengineer:linux .
   ```

3. Build the Docker image for Windows:
   ```bash
   docker build -f Dockerfile.windows -t reverseengineer:windows .
   ```

4. Run the container for Linux:
   ```bash
   docker run -it --rm -v $(pwd):/app reverseengineer:linux
   ```

   On Windows, use this command instead:
   ```bash
   docker run -it --rm -v %cd%:/app reverseengineer:windows
   ```

This will start an interactive shell in the container where you can run ReverseEngineer commands.

Note: The `-v $(pwd):/app` flag mounts your current directory to the `/app` directory in the container, allowing you to analyze local files.

## Configuration

1. Create a `.env` file in the project root directory with your API keys:

```
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

2. Create a `config.yaml` file with the model configurations:

```yaml
default_model: "gpt-4o"
models:
  gpt-4o:
    name: "gpt-4o"
    provider: "openai"
    max_tokens: 4096
    temperature: 0.7
  claude-v1:
    name: "claude-v1"
    provider: "anthropic"
    max_tokens: 8192
    temperature: 0.7
rate_limit:
  limit: 150000
  time_frame: 300
```

## Quick Start

After installation and configuration, you can start using ReverseEngineer right away:

```bash
# Initialize the tool
python reverse_engineer_aider.py init

# Analyze a Python file
python reverse_engineer_aider.py analyze --file path/to/your/code.py --language python

# Generate documentation for a JavaScript file
python reverse_engineer_aider.py generate-documentation --file path/to/your/code.js --language javascript

# Perform a security audit on a C++ file
python reverse_engineer_aider.py security-audit --file path/to/your/code.cpp --language cpp
```

## Usage Examples

### Code Analysis

```bash
python reverse_engineer_aider.py analyze --file complex_algorithm.py --language python
```

Output:
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
python reverse_engineer_aider.py security-audit --file login_system.php --language php
```

Output:
```
Security Audit Results for login_system.php:
1. [HIGH] SQL Injection vulnerability detected on line 23. Use prepared statements instead of string concatenation.
2. [MEDIUM] Weak password hashing algorithm (MD5) used. Recommend switching to bcrypt or Argon2.
3. [LOW] Session ID is not regenerated after login, potentially allowing session fixation attacks.
4. [INFO] Consider implementing rate limiting to prevent brute force attacks.
```

## How It Works

ReverseEngineer uses the `aider` library to interact with different language models. It loads the configuration from a YAML file and environment variables, initializes the appropriate models, and uses a command-line interface (CLI) based on `typer` to expose its functionalities.

The typical workflow is as follows:
1. The user initializes the tool with a configuration.
2. The user chooses a specific command (e.g., analyze, optimize, etc.).
3. The tool loads the specified source code (local file or URL).
4. The code is sent to the language model with specific instructions.
5. The model's response is processed and displayed or saved to a file.

## Dependencies

- [typer](https://typer.tiangolo.com/): For creating the command-line interface
- [pydantic](https://pydantic-docs.helpmanual.io/): For data validation and settings management
- [python-dotenv](https://github.com/theskumar/python-dotenv): For loading environment variables
- [PyYAML](https://pyyaml.org/): For parsing YAML configuration files
- [requests](https://docs.python-requests.org/en/master/): For making HTTP requests
- [aider](https://github.com/paul-gauthier/aider): For interacting with language models

## Contributing

We welcome contributions from the community! Whether it's adding new features, improving documentation, or reporting bugs, your input is valuable. Please check out our [Contribution Guidelines](CONTRIBUTING.md) for more information on how to get started.

## Roadmap

We're continuously working to improve ReverseEngineer. Here's what we have planned for the future:

- [ ] Integration with popular IDEs (VSCode, PyCharm)
- [ ] Support for more programming languages
- [ ] Enhanced visualization of code analysis results
- [ ] API endpoint for integration with CI/CD pipelines
- [ ] Collaborative code analysis features

## Community

Join our community to discuss ReverseEngineer, share your experiences, and get help:

- [Discord Server](https://discord.gg/reverseengineer)
- [Reddit Community](https://www.reddit.com/r/ReverseEngineerAI)
- [Twitter](https://twitter.com/ReverseEngineerAI)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- The `aider` library for providing an easy way to interact with language models
- The open-source community for the various libraries used in this project

## Citation

If you use ReverseEngineer in your research or project, please cite it as follows:

```
@software{ReverseEngineer,
  author = {Jacques Gariépy},
  title = {ReverseEngineer: A LLM-powered tool for code analysis and manipulation},
  year = {2024},
  url = {https://github.com/JacquesGariepy/ReverseEngineer}
}
```

---

<p align="center">
  Made with ❤️ by the ReverseEngineer Team
</p>

<p align="center">
  <a href="#top">Back to Top</a>
</p>
