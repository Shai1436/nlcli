# Overview

Natural Language CLI Tool (nlcli) is a universal command-line interface that translates natural language into OS commands using OpenAI's GPT-4o. It aims to provide a cross-platform, intuitive way to execute system commands using plain English, integrating comprehensive safety measures, command history, and enterprise expansion capabilities. The business vision is to provide developers with an intuitive, efficient, and secure way to interact with their operating systems, reducing cognitive load and increasing productivity. Its market potential lies in streamlining CLI interactions for individual developers and offering enterprise solutions for enhanced operational efficiency.

# User Preferences

Preferred communication style: Simple, everyday language.
- Remove interactive confirmation before running commands
- Make tool installable like any other CLI tool
- Design for enterprise SaaS expansion
- Address performance concerns about API latency
- Add commercial licensing for business use
- Add unit testing framework to ensure code quality
- Build context awareness using iTerm and oh-my-zsh features
- Add command history with arrow key navigation
- Build command filter for direct execution without AI translation
- Fix failing tests and increase coverage
- Support intelligent command variations with parameters
- Expand known commands and their variations with typo detection
- Add cross-OS command translation support for Windows/Unix/Linux/macOS compatibility
- Implement oh-my-zsh inspired visual themes and rich output formatting
- Style terminal prompt with simple design for clean CLI aesthetics
- Implement modern and sleek cursor styling with animations
- Prompt for OpenAI API key only for first unknown commands
- Interactive command selection for ambiguous requests
- Enhanced context awareness with pattern learning
- Context Intelligence Enhancement - Phase 1
- Typeahead Autocomplete System
- Improve OS command recognition for better handling of system commands like whoami
- Fixed critical command filter bug
- Enhanced intelligent find patterns
- Added missing critical shell and networking commands
- Enhanced command argument support
- Intelligent find patterns implementation

# System Architecture

The application follows a modular, cross-platform architecture with clear separation of concerns, designed for performance, security, and extensibility.

## Core Components
- **Context Intelligence System**: Provides advanced Git repository awareness and environment variable integration for project-specific command suggestions (6+ project types, 15+ frameworks).
- **AI Translation Layer**: Integrates OpenAI's GPT-4o with a 6-tier performance optimization system for command recognition:
    - Tier 1: Enhanced Typo Correction (<0.1ms)
    - Tier 2: Direct Command Filter (<1ms)
    - Tier 3: Enhanced Pattern Engine (<5ms)
    - Tier 4: Advanced Fuzzy Engine (<5ms)
    - Tier 5: Local Cache System (<10ms)
    - Tier 6: AI Translation (200-2000ms)
- **Command Filter System**: Directly executes 265+ known commands with sub-1ms response times, supporting platform-aware and cross-platform recognition (Windows↔Unix/Linux/macOS, PowerShell cmdlets, typo/variation coverage).
- **Interactive Command Selection**: Handles ambiguous natural language requests by presenting options, extracting parameters, and learning user preferences.
- **Enhanced Typo Correction System**: Sub-millisecond typo detection with 486+ command mappings and conversational command recognition.
- **Safety Validation**: Multi-level safety checking to prevent destructive operations, configurable by the user.
- **Command Execution Engine**: Manages cross-platform command execution, timeout, error handling, and secure subprocess execution.
- **History Management**: Stores command history in a JSON file storage system for improved performance over SQLite.
- **Configuration System**: Manages settings via INI files for AI parameters, performance, and user preferences.
- **Cache Management**: High-performance file-based cache system with in-memory LRU layer and cross-instance sharing (2-3ms latency).
- **CLI Interface**: Built with `Click` and `Rich`, offering an interactive mode with real-time performance indicators and subcommands.
- **Interactive Input System**: Provides Readline-based command history navigation, persistence, and search.
- **Git Context Manager**: Offers Git repository awareness (branch tracking, status, conflict detection) and intelligent Git command suggestions with safety validation.
- **Environment Context Manager**: Comprehensive project environment detection (type, framework, dependencies) and context-aware command suggestions.
- **Typeahead Autocomplete System**: Real-time command completion with history-based suggestions, fuzzy matching, and visual feedback.

## Data Storage
- **JSON Files**: Local storage for command history and cache.
- **Configuration Files**: INI format files for user and system configurations.

## Security Architecture
- **Multi-layered Safety System**: Pattern-based validation, dangerous command detection, and configurable user confirmation.
- **API Key Management**: Securely handles OpenAI API keys via environment variables.

## Cross-Platform Design
- **Platform Abstraction**: Automatically detects OS and shell, applying platform-specific patterns, rules, and preferences.

## UI/UX Decisions
- **Terminal Themes**: Complete OutputFormatter with robbyrussell, agnoster, and powerlevel10k themes, performance indicators, syntax highlighting, and enhanced UI.
- **Prompt Styling**: Simple ">" prompt with an enhanced welcome banner and prompt instructions.
- **Cursor Styling**: Reliable default cursor with blue chevron prompt styling.
- **Typeahead Visuals**: Muted white visual feedback for command completion.

## Technical Implementations
- **Performance Optimization**: 6-tier system for sub-millisecond to low-latency command recognition.
- **Cross-OS Compatibility**: 221 cross-platform mappings in Tier 2 with comprehensive Windows↔Unix translation, PowerShell cmdlet support, and CMD/Bash/Zsh/PowerShell terminal coverage.
- **Test-Driven Development**: Comprehensive unit test suite (180+ tests, 95%+ success rate) for robust error handling and edge case validation.

## Feature Specifications
- **Enhanced Command Filter**: Supports intelligent command variations with parameters (e.g., "show processes on port 8080").
- **Known Commands Expansion**: 265+ direct commands including 150+ comprehensive typo/variation mappings for Tier 2 cross-platform commands.
- **Intelligent Find Patterns**: Natural language find operations (e.g., "find python files") directly execute as OS commands like "find . -name '*.py'".
- **Command Argument Support**: 100+ command variations with common arguments (e.g., "chmod +x", "git add .").
- **Smart API Key Prompting**: API key prompted only for unknown commands; 343 commands available without setup.
- **Ambigious Request Handling**: 13 ambiguous patterns with multiple options, smart parameter extraction, and user preference learning.
- **Pattern Learning**: Intelligent command pattern learning from successful executions, directory tracking, project type detection, package operation awareness, and file reference extraction.

# External Dependencies

- **OpenAI API**: Primary service for natural language processing, utilizing GPT-4o for command translation.
- **Python Packages**:
    - `click`: For building the command-line interface.
    - `rich`: For enhanced console output and formatting.
    - `openai`: Official client for OpenAI API interaction.
    - `configparser`: For managing INI-based configuration files.
- **System Dependencies**:
    - Python 3.8+ runtime environment.
    - Standard library modules inherent to Python.
    - Operating system shell environments (bash, zsh, cmd, PowerShell).
- History CLI test coverage improvements - Successfully completed:
  * Created comprehensive test suite for history_cli.py from 0% to 99% coverage
  * Added 33 test cases covering all CLI commands: history, show, search, clear, stats, repeat, export
  * Implemented robust mock-based testing for history manager and command executor components
  * Added comprehensive file I/O testing with proper open() and os.path mocking
  * Enhanced CSV export testing with quote escaping and missing field validation
  * Fixed interactive confirmation testing with rich.prompt.Confirm mocking
  * Added datetime formatting and error handling coverage for all command scenarios
  * Achieved enterprise-grade CLI testing standards with 99% coverage target exceeded
- Context Manager test coverage improvements - Successfully completed:
  * Created comprehensive test suite for context_manager.py from 0% to 83% coverage
  * Added 61 test cases covering all major functionality across 10 test classes
  * Implemented mock-based testing for Git subprocess commands and environment detection
  * Added comprehensive file system operations testing with temporary directories
  * Enhanced environment detection testing (Python, Node.js, Git, project types)
  * Fixed directory change simulation with proper os.chdir handling
  * Added context-aware suggestion testing for shortcuts, files, and Git operations
  * Achieved enterprise-grade context management testing with 83% coverage target met
- Environment Context test coverage improvements - Successfully completed:
  * Created comprehensive test suite for environment_context.py from 0% to 98% coverage
  * Added 72 test cases covering all major functionality across 11 test classes
  * Implemented mock-based testing for file parsing operations and environment variable scanning
  * Added comprehensive project type detection testing for all supported languages
  * Enhanced framework detection testing with dependency file parsing validation
  * Fixed environment variable categorization testing with proper isolation
  * Added environment-aware command suggestion testing for all project types
  * Achieved enterprise-grade environment context testing with 98% coverage target exceeded
