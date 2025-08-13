# Overview

Natural Language CLI Tool (nlcli) is a universal command-line interface that translates natural language into OS commands using OpenAI's GPT-4o. The tool is designed as a cross-platform solution that works on Linux, macOS, and Windows, providing users with an intuitive way to execute system commands using plain English. The application includes comprehensive safety measures, command history tracking, and is built with enterprise expansion capabilities in mind.

# User Preferences

Preferred communication style: Simple, everyday language.

## Recent User Requests
- Remove interactive confirmation before running commands (implemented: auto-execute read-only commands)
- Make tool installable like any other CLI tool (implemented: pip installable with console scripts)
- Design for enterprise SaaS expansion (architecture supports this)
- Address performance concerns about API latency (implemented: 3-tier performance optimization system)
- Add commercial licensing for business use (implemented: Personal Developer/Commercial license structure targeting individual developers)
- Add unit testing framework to ensure code quality (implemented: comprehensive test suite with instant pattern validation)
- Build context awareness using iTerm and oh-my-zsh features (implemented: comprehensive context system with 60+ shortcuts)
- Add command history with arrow key navigation (implemented: interactive input with readline support)
- Build command filter for direct execution without AI translation (implemented: 70+ direct commands with sub-5ms performance)
- Fix failing tests and increase coverage (implemented: 38% overall coverage, fixed 12+ test failures, API consistency improvements)
- Support intelligent command variations with parameters (implemented: Enhanced command filter with regex patterns and parameter detection for commands like "show processes on port 8080")
- Implement oh-my-zsh inspired visual themes and rich output formatting (implemented: Complete OutputFormatter with robbyrussell, agnoster, and powerlevel10k themes, performance indicators, syntax highlighting, and enhanced UI)

## Approved Roadmap & Next Features

Based on current implementation, the next logical features are prioritized as:

**Immediate Priority (Next 2 weeks):**
1. **Advanced Pattern Recognition** - Expand from 15 to 60+ instant command patterns (COMPLETED)
2. **Command Context Awareness** - Remember current directory, previous commands for better suggestions (COMPLETED)
3. **Interactive Command History** - Arrow key navigation, search, management commands (COMPLETED)
4. **Enhanced Output Formatting** - Rich display with colors, tables, and better visual presentation (COMPLETED)
5. **Interactive Command Selection** - When multiple commands possible, let user choose

**Short Term (2-4 weeks):**
1. **Command Templates & Sharing** - Pre-approved patterns for teams
2. **Configuration Profiles** - Multiple user profiles for different contexts
3. **Command Chaining** - Support for complex multi-step operations
4. **Undo/Redo System** - Reverse previous commands where possible

**Medium Term (1-3 months):**
1. **REST API & Plugin System** - Enterprise integrations and extensibility
2. **Web Dashboard** - Browser-based management interface
3. **Advanced Security & Compliance** - Audit logging and enterprise security
4. **SSO Integration** - Enterprise authentication systems

**V2.0 Future Features:**
1. **Cross-OS Dotfile Management** - Unified profile system handling per-OS differences (PATH, aliases, PowerShell vs .zshrc)
2. **Git/Stow Integration** - Version control integration for dotfile synchronization
3. **Cloud/Local Sync** - One source of truth for configurations across machines and operating systems
4. **Template System** - OS-specific configuration templates that adapt to current platform context

Full roadmap available in [ROADMAP.md](ROADMAP.md)

## Development Workflow

**Test-Driven Development**
- Comprehensive unit test suite with 95+ instant pattern tests
- Automated test runner (`test_automation.py`) for continuous validation
- Tests run after each major change to ensure quality
- Pattern recognition tests validate 100% match rate for common commands
- Test categories: instant patterns, AI translation, safety checking, command execution

**Quality Assurance Process**
1. Write tests first for new features
2. Implement feature with pattern expansion
3. Run automated test suite (`python test_automation.py`)
4. Validate pattern match rates and performance
5. Update documentation and roadmap

# System Architecture

## Core Components

The application follows a modular architecture with clear separation of concerns:

**AI Translation Layer** (`ai_translator.py`)
- 4-tier performance optimization system for maximum speed:
  1. **Direct Command Filter** (sub-5ms): 70+ exact commands bypass AI completely
  2. **Instant Pattern Matching** (sub-millisecond): 60+ common commands recognized immediately
  3. **Local SQLite Cache** (sub-millisecond): Stores and retrieves previous translations
  4. **AI Translation** (2-3 seconds): GPT-4o-mini with timeout and concurrent execution
- Integrates with OpenAI's GPT-4o-mini API for faster responses
- Uses platform-specific prompts to generate appropriate OS commands
- Returns structured responses with command, explanation, and confidence scores
- Performance monitoring with response time indicators
- Handles API authentication and error management

**Command Filter System** (`command_filter.py`, `filter_cli.py`)
- Direct execution of 70+ known commands without AI translation
- Platform-aware command recognition (Linux/macOS/Windows)
- Sub-5ms response times with 100% confidence scores
- Support for exact matches, predefined arguments, and custom arguments
- Comprehensive CLI management: stats, list, suggest, add, remove, test, benchmark
- Custom command support for user-defined mappings
- Performance monitoring and statistics tracking

**Safety Validation** (`safety_checker.py`)
- Implements multi-level safety checking (low, medium, high)
- Maintains platform-specific dangerous command patterns
- Prevents execution of destructive operations like `rm -rf /` or registry modifications
- Configurable safety levels for different user requirements

**Command Execution Engine** (`command_executor.py`)
- Cross-platform command execution with proper shell detection
- Timeout management and error handling
- Secure subprocess execution with output capturing
- Working directory and environment variable support

**History Management** (`history_manager.py`, `history_cli.py`)
- SQLite-based storage for command history with comprehensive CLI management
- Tracks natural language inputs, generated commands, and execution results
- Indexed for efficient querying and retrieval
- Session management for organizing command history
- Rich CLI commands: show, search, clear, stats, repeat, export
- Integration with interactive input for seamless history navigation

**Configuration System** (`config_manager.py`)
- INI-based configuration with sensible defaults
- Manages AI settings (model, temperature, timeouts)
- Performance optimization settings (cache, patterns, timeouts)
- User preferences for safety levels and interface behavior
- Platform-specific configuration paths

**Cache Management** (`cache_manager.py`)
- SQLite-based local cache for translation results
- Platform-aware caching with input normalization
- Usage statistics and popular command tracking
- Automatic cleanup of old entries
- Cache hit rate monitoring for performance optimization

**CLI Interface** (`main.py`)
- Click-based command-line interface with Rich console output
- Interactive mode for real-time command translation with history navigation
- Real-time performance indicators (⚡ instant, 🎯 context-aware, 📋 cached, 🤖 AI)
- Performance monitoring command (`nlcli performance`)
- Subcommand structure for extensibility
- Context management for sharing components across commands

**Interactive Input System** (`interactive_input.py`)
- Readline-based command history with up/down arrow key navigation
- Persistent history storage in `~/.nlcli/input_history`
- Command completion and search functionality
- Cross-platform fallback for systems without readline
- Integration with database history for seamless experience

## Data Storage

**SQLite Database**
- Local storage for command history
- Schema includes natural language input, generated commands, execution success, and timestamps
- Indexed for performance on timestamp and platform fields
- Backup and maintenance capabilities

**Configuration Files**
- INI format configuration stored in user's home directory
- Hierarchical settings with defaults and user overrides
- Separate sections for AI, storage, and general preferences

## Security Architecture

**Multi-layered Safety System**
- Pattern-based command validation before execution
- Platform-aware dangerous command detection
- User confirmation prompts for potentially risky operations
- Configurable safety levels from permissive to restrictive

**API Key Management**
- Environment variable-based OpenAI API key storage
- Secure handling without logging sensitive information
- Graceful error handling for missing or invalid keys

## Cross-Platform Design

**Platform Abstraction**
- Automatic detection of operating system and shell environment
- Platform-specific command patterns and safety rules
- Shell preference handling (bash, zsh, cmd, PowerShell)
- Path and directory management across different filesystems

# External Dependencies

**OpenAI API**
- Primary dependency for natural language processing
- Uses GPT-4o model for command translation
- Requires API key authentication
- Configurable timeout and token limits

**Python Packages**
- `click`: Command-line interface framework
- `rich`: Enhanced console output and formatting
- `openai`: Official OpenAI API client
- `configparser`: Configuration file management
- `sqlite3`: Built-in database functionality (no external dependency)

**System Dependencies**
- Python 3.8+ runtime environment
- Standard library modules for cross-platform operation
- Operating system shell environments (bash, zsh, cmd, PowerShell)

**Development and Distribution**
- `setuptools`: Package distribution and installation
- PyPI integration for package distribution
- Install scripts for different platforms (bash, PowerShell)