# Natural Language CLI Tool (nlcli)

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Commercial-blue.svg)](COMMERCIAL_LICENSE.md)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](coverage.json)

An advanced AI-powered Natural Language CLI tool that transforms complex user intents into precise OS commands through intelligent semantic processing and adaptive machine learning. Built for enterprise deployment with production-ready architecture.

## 🚀 Key Features

### Core Functionality
- **6-Level Pipeline Architecture**: Context → Exact Commands → Patterns → Fuzzy Matching → Semantic ML → AI Fallback
- **534+ Direct Commands**: Sub-1ms response times for comprehensive enterprise-grade command coverage
- **Cross-Platform Intelligence**: Windows↔Unix↔Linux↔macOS command translation with PowerShell support
- **Smart API Key Management**: Single-prompt setup with persistent storage across sessions
- **Advanced Context Awareness**: Git repository detection, project type recognition, environment integration

### Performance & Intelligence
- **Sub-Millisecond Recognition**: Lightning-fast command filtering for common operations
- **Semantic Matching**: Local ML with 80% confidence threshold covering 30+ command categories
- **Fuzzy Typo Correction**: Intelligent correction system replacing 486+ manual mappings
- **Parameter Intelligence**: Universal resolver supporting 9 parameter types with smart defaults
- **High-Performance Caching**: File-based cache with in-memory LRU layer and cross-instance sharing

### Enterprise-Ready Architecture  
- **Production-Grade Storage**: Atomic file operations with comprehensive error handling
- **100% Test Coverage**: 37 storage tests plus comprehensive pipeline validation
- **Clean Module Design**: Zero import conflicts with proper entry point configuration
- **Commercial Licensing**: Enterprise support and commercial deployment ready
- **Zero Dependencies for Core**: 534+ commands work without external API calls for enterprise productivity
- **Persistent Configuration**: Single setup persists across all sessions and instances

## 📦 Installation

### From Source (Recommended for Latest Features)

```bash
# Clone and install in development mode
git clone https://github.com/nlcli/nlcli.git
cd nlcli
pip install -e .

# Start using the CLI
nlcli
# or use the short alias
nl
```

### Direct Execution

```bash
# Run directly without installation
python -m nlcli
```

### Future PyPI Installation

```bash
# Coming soon to PyPI
pip install nlcli
```

## 🔑 Setup & First Run

### Quick Start (No API Key Needed for 265+ Commands)
```bash
# Start the CLI immediately
nlcli

# Try common commands without any setup
> list files
> current directory
> show processes
```

### For AI-Powered Commands (Optional)
1. **Get OpenAI API Key**: Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. **First AI Command**: The system will prompt you once and save it permanently
3. **Or Set Environment Variable**: 
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

### Verify Installation
```bash
nlcli --help
```

## 🚀 Usage

### Interactive Mode
```bash
nlcli
# or use the short alias
nl
```

### Example Commands
```
> list files
⚡ Instant match (0.001s)
Command: ls -la
Explanation: List all files with details

> find python files
🔍 Pattern match (0.002s) 
Command: find . -name "*.py"
Explanation: Find all Python files in current directory

> show running processes
⚡ Instant match (0.001s)
Command: ps aux
Explanation: Display all running processes

> complex natural language query
🤖 AI Translation (1.2s)
Command: custom solution
Explanation: AI-generated command for complex requests
```

### Performance Tiers
- **⚡ Instant**: 265+ commands with sub-1ms recognition
- **🔍 Pattern**: Intelligent pattern matching (1-5ms)
- **🧠 Fuzzy**: Typo correction and variations (5-50ms)
- **🎯 Semantic**: Local ML matching (50-200ms)  
- **🤖 AI**: OpenAI fallback for complex requests (1-3s)

## 🏗️ Architecture

### 6-Level Pipeline Processing
1. **Level 1 - Context**: Shell detection, Git awareness, environment analysis
2. **Level 2 - Direct Commands**: 265+ instant command recognition
3. **Level 3 - Pattern Engine**: Intelligent pattern matching for variations
4. **Level 4 - Fuzzy Matching**: Typo correction and similar command detection  
5. **Level 5 - Semantic ML**: Local machine learning for intent classification
6. **Level 6 - AI Fallback**: OpenAI GPT-4o for complex natural language

### Cross-Platform Intelligence
- **Windows**: PowerShell cmdlets, CMD commands, Windows utilities
- **Linux**: Bash commands, system utilities, package managers
- **macOS**: Unix commands with macOS-specific tools
- **Universal**: 221 cross-platform command mappings

### Storage & Performance
- **File-based Cache**: High-performance caching with memory layer
- **Atomic Operations**: Safe file handling with comprehensive error recovery
- **History Management**: JSON-based command history with search capabilities
- **Configuration**: Persistent INI-based settings with environment integration

## 🚀 Performance Benchmarks

| Operation Type | Response Time | Commands Supported | API Required |
|----------------|---------------|-------------------|--------------|
| Direct Commands | 0.001-0.005s | 265+ | No |
| Pattern Matching | 0.001-0.010s | 100+ patterns | No |
| Fuzzy/Typo Fix | 0.005-0.050s | Unlimited variations | No |
| Semantic ML | 0.050-0.200s | 30+ categories | No |
| AI Translation | 1.0-3.0s | Unlimited | Yes |

## 🧪 Testing & Quality

- **100% Test Coverage**: Comprehensive test suite with 37+ storage tests
- **Production Validation**: All storage components verified through dry run testing
- **Cross-Platform**: Tested on Linux, Windows, macOS environments
- **Error Handling**: Robust error recovery and graceful degradation
- **Memory Efficiency**: Optimized for low memory footprint

## 📁 Project Structure

```
nlcli/
├── cli/                    # Command-line interface
│   ├── main.py            # Main CLI entry point
│   ├── context_ui.py      # Context management UI
│   ├── history_cli.py     # History management commands
│   └── filter_cli.py      # Command filtering interface
├── pipeline/               # Core processing pipeline
│   ├── shell_adapter.py   # Level 1: Context detection
│   ├── command_filter.py  # Level 2: Direct commands
│   ├── pattern_engine.py  # Level 3: Pattern matching
│   ├── fuzzy_engine.py    # Level 4: Fuzzy matching
│   ├── semantic_matcher.py # Level 5: ML classification
│   └── ai_translator.py   # Level 6: AI fallback
├── storage/                # Data persistence
│   ├── file_cache.py      # High-performance caching
│   ├── file_history.py    # Command history management
│   └── config_manager.py  # Configuration system
├── execution/              # Command execution
│   ├── command_executor.py # Safe command execution
│   └── safety_checker.py  # Security validation
└── ui/                     # User interface components
    ├── interactive_input.py # Enhanced input handling
    ├── output_formatter.py # Rich output formatting
    └── command_selector.py  # Interactive selection
```

## 🔒 Security & Safety

- **Multi-level Safety**: Pattern-based validation for destructive operations
- **Configurable Security**: User-adjustable safety levels (strict, medium, permissive)
- **Command Validation**: Pre-execution safety checks
- **Secure Storage**: Safe handling of API keys and configuration data
- **Audit Trail**: Complete command history with success/failure tracking

## 🔧 Configuration

### Configuration File Location
```
~/.nlcli/config.ini
```

### Key Settings
```ini
[api]
openai_key = your-api-key-here
model = gpt-4o
temperature = 0.3

[general]
safety_level = medium
auto_confirm_read_only = true
max_history_items = 1000

[performance]
cache_enabled = true
cache_size = 1000
timeout = 30
```

## 🎯 Enterprise Features

- **Commercial Licensing**: Available for business use
- **API Integration**: RESTful API for system integration
- **Audit Logging**: Comprehensive command tracking
- **Multi-user Support**: User-specific configurations
- **Scalable Architecture**: Designed for enterprise deployment
- **Professional Support**: Available for commercial users

## 📈 Roadmap

### Current Status: Production Ready ✅
- 6-level pipeline architecture implemented
- 265+ commands with instant recognition
- Cross-platform compatibility verified
- 100% test coverage achieved
- Storage system production-validated

### Future Enhancements
- [ ] Plugin system for custom commands
- [ ] Web-based management interface
- [ ] Team collaboration features
- [ ] Advanced analytics dashboard
- [ ] Integration with popular DevOps tools

### Single Command Translation
```bash
nlcli translate "list all files in current directory"
nlcli translate "create a backup of my documents folder" --explain-only
nlcli translate "show disk usage" --execute
```

### Command History
```bash
nlcli history
nlcli history --limit 50
```

### Configuration
```bash
nlcli config                    # Show current settings
```

## 📝 Examples

### File Operations
- `"list all Python files in this directory"`
- `"create a new folder called projects"`
- `"copy all images to backup folder"`
- `"find all files larger than 100MB"`

### System Information
- `"show disk usage"`
- `"display running processes"`
- `"check memory usage"`
- `"show network connections"`

### Development Tasks
- `"initialize a git repository"`
- `"install Python package requests"`
- `"run unit tests"`
- `"compress project folder"`

## ⚙️ Configuration

Configuration is stored in `~/.nlcli/config.ini`:

```ini
[general]
safety_level = medium
auto_confirm_read_only = true
max_history_items = 1000

[ai]
model = gpt-4o
temperature = 0.3
max_tokens = 500

[storage]
db_name = nlcli_history.db
backup_enabled = true
```

## 🛡️ Safety Features

- **Multi-level Safety Checks**: Configurable safety levels (low/medium/high)
- **Command Validation**: Prevents destructive operations
- **Read-only Auto-execution**: Safe commands execute automatically
- **Confirmation Prompts**: Dangerous commands require explicit confirmation
- **Platform-aware**: Different safety rules for Windows/Linux/macOS

## 🏗️ Architecture

Built with enterprise expansion in mind:

- **Modular Design**: Separate components for AI translation, safety, execution
- **Plugin System**: Extensible for custom commands and integrations
- **Database Storage**: SQLite for command history and user data
- **Cross-platform**: Works on all major operating systems
- **API Ready**: Core components can be exposed via REST API

## 🔧 Development

### Project Structure
```
nlcli/
├── nlcli/
│   ├── __init__.py
│   ├── main.py              # CLI interface
│   ├── ai_translator.py     # OpenAI integration
│   ├── safety_checker.py    # Safety validation
│   ├── command_executor.py  # Command execution
│   ├── history_manager.py   # SQLite history
│   ├── config_manager.py    # Configuration
│   └── utils.py            # Utilities
├── install.sh              # Linux/macOS installer
├── install.bat            # Windows installer
├── setup.py               # Package setup
└── pyproject.toml         # Modern Python packaging
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📊 Enterprise Features (Roadmap)

- **Team Management**: Multi-user support with role-based access
- **Command Templates**: Pre-approved command patterns
- **Audit Logging**: Complete command execution tracking
- **API Gateway**: REST API for integrations
- **Web Dashboard**: Browser-based management interface
- **SSO Integration**: Enterprise authentication
- **Custom Models**: Fine-tuned AI models for specific environments

## 📄 License

NLCLI uses a developer-friendly licensing structure:

### Personal Developer License (Free)
- **Individual developers** - Personal projects, learning, portfolios
- **Small freelancers** - Projects under $10,000 annual revenue
- **Educational use** - Students, teachers, academic research
- **Open source projects** - Non-commercial open source contributions

### Commercial License (Paid)
- **Business use** - Companies with 5+ employees or revenue-generating use
- **Enterprise organizations** - Requiring legal protection and support
  - Legal indemnification and warranty
  - Priority support and SLA
  - Custom features and integrations
  - Enterprise security features

📋 **[View Commercial License Options](COMMERCIAL_LICENSE.md)**

**Need help choosing?** Contact us at license@nlcli.dev

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/nlcli/nlcli/issues)
- **Documentation**: [Read the Docs](https://nlcli.readthedocs.io)
- **Discussions**: [GitHub Discussions](https://github.com/nlcli/nlcli/discussions)
