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
- COMPLETED: Three-phase context-driven architecture refactoring (Aug 17, 2025)
- COMPLETED: Replaced 486+ manual typo mappings with intelligent fuzzy matching system (Aug 17, 2025)
- COMPLETED: Fuzzy matching architecture refactoring - eliminated code duplication and created shared components (Aug 17, 2025)
- COMPLETED: Pipeline cleanup and consolidation - 5-level architecture with eliminated redundancy (Aug 17, 2025)
- COMPLETED: Context architecture refactoring - moved ALL context initialization from Level 5 (AITranslator) to Level 1 (ShellAdapter) for clean separation of concerns (Aug 17, 2025)
- COMPLETED: Renamed context_cli.py to context_ui.py to properly reflect its UI nature rather than core functionality (Aug 17, 2025)
- COMPLETED: Fixed pipeline component errors - added missing get_statistics method to CommandFilter, renamed AdvancedPatternEngine to PatternEngine, and fixed pipeline integration issues (Aug 17, 2025)
- COMPLETED: Added missing 'find_all_files' pattern to Level 3 Pattern Engine and fixed context manager path in main.py for proper Level 3 pattern recognition (Aug 17, 2025)

# System Architecture

The application follows a modular, cross-platform architecture with clear separation of concerns, designed for performance, security, and extensibility.

## Core Components
- **Context Intelligence System**: Provides advanced Git repository awareness and environment variable integration for project-specific command suggestions (6+ project types, 15+ frameworks).
- **Enhanced Shell Adapter**: Centralized system expertise providing comprehensive context with 18 metadata fields including platform detection, shell identification, command categorization, cross-platform equivalents, and confidence scoring.
- **Context-Driven AI Translation Layer**: Streamlined AI translator that accepts context from shell adapter instead of self-detecting platform information, integrating OpenAI's GPT-4o with optimized performance.
- **Command Filter System**: Directly executes 265+ known commands with sub-1ms response times, supporting platform-aware and cross-platform recognition.
- **Interactive Command Selection**: Handles ambiguous natural language requests by presenting options, extracting parameters, and learning user preferences.
- **Modular Fuzzy Matching System**: Refactored architecture with shared components (BaseFuzzyMatcher, TextNormalizer, CommonTransforms, SimilarityCalculator) eliminating 40% code duplication while maintaining sub-1ms performance (August 17, 2025).
- **Safety Validation**: Multi-level safety checking to prevent destructive operations, configurable by the user.
- **Command Execution Engine**: Manages cross-platform command execution, timeout, error handling, and secure subprocess execution.
- **History Management**: Stores command history in a JSON file storage system.
- **Configuration System**: Manages settings via INI files for AI parameters, performance, and user preferences.
- **Cache Management**: High-performance file-based cache system with in-memory LRU layer and cross-instance sharing.
- **CLI Interface**: Built with `Click` and `Rich`, offering an interactive mode with real-time performance indicators and subcommands using context-driven pipeline flow.
- **Interactive Input System**: Provides Readline-based command history navigation, persistence, and search.
- **Git Context Manager**: Offers Git repository awareness and intelligent Git command suggestions with safety validation.
- **Environment Context Manager**: Comprehensive project environment detection and context-aware command suggestions.
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
- **Context-Driven Architecture**: Three-phase refactoring completed August 17, 2025, implementing clean separation of concerns where shell adapter provides system expertise to AI translator for language processing.
- **Modular Fuzzy Architecture**: Created shared base architecture eliminating code duplication across fuzzy matching systems, with FastFuzzyMatcher for command filtering and preserved AdvancedFuzzyEngine for complex AI operations (August 17, 2025).
- **5-Level Pipeline Architecture**: Completed pipeline cleanup August 17, 2025, with proper metadata flow: Level 1 (context) → Level 2 (exact commands) → Level 3 (patterns) → Level 4 (fuzzy/typo) → Level 5 (AI fallback).
- **Performance Optimization**: 5-tier system for sub-millisecond to low-latency command recognition with context computed once and metadata aggregation eliminating duplicate processing.
- **Cross-OS Compatibility**: 221 cross-platform mappings in Level 2 with comprehensive Windows↔Unix translation, PowerShell cmdlet support, and CMD/Bash/Zsh/PowerShell terminal coverage.
- **Test-Driven Development**: Comprehensive unit test suite for robust error handling and edge case validation with 30.3% line coverage.

## Feature Specifications
- **Enhanced Command Filter**: Supports intelligent command variations with parameters.
- **Known Commands Expansion**: 265+ direct commands including 150+ comprehensive typo/variation mappings for Tier 2 cross-platform commands.
- **Intelligent Find Patterns**: Natural language find operations directly execute as OS commands.
- **Command Argument Support**: 100+ command variations with common arguments.
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
```