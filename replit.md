# Overview

The Natural Language CLI Tool (nlcli) is an AI-powered universal command-line interface designed to convert natural language intents into precise OS commands. It features a production-ready 6-level pipeline architecture, offering sub-1ms response times for 265+ direct commands, cross-platform compatibility, and core functionality with zero external dependencies. The primary goal is to enhance developer and enterprise productivity by providing an intuitive, efficient, and secure interaction with operating systems through intelligent command translation, comprehensive safety measures, and a scalable architecture.

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
- **CRITICAL**: Resolved Windows PowerShell deployment and compatibility issues (v1.1.1)
- Clean Windows installation without fann2/padatious dependency conflicts
- **ARCHITECTURE PLAN**: Shared Parameterized Pipeline Design
  - Base command matching across all pipeline levels (network, status, etc.)
  - Shared parameter context flows between levels {platform, shell, etc.}
  - Each pipeline level can resolve to parameterized version when needed
  - Preserves pipeline matching while enabling context-aware command generation
- **PENDING FIX**: Pipeline context initialization timing issue
  - Pattern engine initialization happens before shell adapter context available
  - Command templates baked in at class creation, can't adapt to runtime context
  - Need two-phase approach: defer command generation until pipeline execution

# System Architecture

The application employs a modular, cross-platform architecture emphasizing performance, security, and extensibility with clear separation of concerns.

## Core Components
- **Context Intelligence System**: Provides Git repository awareness and environment variable integration for project-specific command suggestions.
- **Enhanced Shell Adapter**: Centralized system expertise delivering comprehensive context, including platform detection, shell identification, and command categorization.
- **Context-Driven AI Translation Layer**: Integrates OpenAI's GPT-4o, accepting context from the shell adapter for optimized performance.
- **Command Filter System**: Directly executes over 534 known commands with sub-1ms response times, supporting platform-aware and cross-platform recognition including comprehensive destructive command safety patterns.
- **Common Parameter Resolver**: Universal parameter extraction and validation system supporting 9 parameter types (e.g., size, port, host) with intelligent defaults and regex validation.
- **Interactive Command Selection**: Manages ambiguous natural language requests by presenting options and learning user preferences.
- **Modular Fuzzy Matching System**: Refactored architecture eliminating code duplication while maintaining sub-1ms performance.
- **Safety Validation**: Multi-level safety checking to prevent destructive operations.
- **Command Execution Engine**: Manages cross-platform command execution, timeout, error handling, and secure subprocess execution.
- **History Management**: Stores command history locally.
- **Configuration System**: Manages settings via INI files for AI parameters and user preferences.
- **Cache Management**: High-performance file-based cache with in-memory LRU layer.
- **CLI Interface**: Built with `Click` and `Rich`, offering an interactive mode with real-time performance indicators.
- **Interactive Input System**: Provides Readline-based command history navigation, persistence, and search.
- **Git Context Manager**: Offers Git repository awareness and intelligent Git command suggestions.
- **Environment Context Manager**: Comprehensive project environment detection.
- **Typeahead Autocomplete System**: Real-time command completion with history-based suggestions and fuzzy matching.

## Data Storage
- **JSON Files**: For local command history and cache.
- **Configuration Files**: INI format for configurations.

## Security Architecture
- **Multi-layered Safety System**: Includes pattern-based validation and dangerous command detection.
- **API Key Management**: Securely handles OpenAI API keys via environment variables.

## Cross-Platform Design
- **Platform Abstraction**: Automatically detects OS and shell, applying platform-specific rules.

## UI/UX Decisions
- **Terminal Themes**: OutputFormatter with themes like robbyrussell, agnoster, and powerlevel10k, including syntax highlighting.
- **Prompt Styling**: Simple ">" prompt with welcome banner.
- **Cursor Styling**: Default cursor with blue chevron styling.
- **Typeahead Visuals**: Muted white visual feedback for command completion.

## Technical Implementations
- **Context-Driven Architecture**: Clean separation of concerns where the shell adapter provides system expertise to the AI translator.
- **Modular Fuzzy Architecture**: Shared base architecture for fuzzy matching systems, optimized for both command filtering and complex AI operations.
- **6-Level Pipeline Architecture**: Level 1 (context) → Level 2 (exact commands) → Level 3 (patterns) → Level 4 (fuzzy/typo) → Level 5 (semantic ML) → Level 6 (AI fallback).
- **Universal Parameter System**: Common Parameter Resolver integrated across all pipeline levels with intelligent extraction patterns and validation rules.
- **Shared Parameterized Pipeline**: Base command matching preserved across all levels with shared context {platform, shell} for runtime command resolution.
- **Performance Optimization**: 5-tier system for sub-millisecond to low-latency command recognition.
- **Cross-OS Compatibility**: Comprehensive Windows↔Unix translation and terminal coverage (CMD, Bash, Zsh, PowerShell).
- **Production-Ready Storage System**: High-performance file-based caching, atomic file operations, and accurate command history statistics.
- **Clean Module Architecture**: Resolved import conflicts and implemented a clean execution path.
- **Comprehensive Test Suite**: Robust testing with high pass rates for error handling and edge cases.

## Feature Specifications
- **Enhanced Command Filter**: Supports intelligent command variations with parameters.
- **Known Commands Expansion**: Over 534 direct commands (342 base + 192 variations), including comprehensive typo/variation mappings and destructive command safety patterns.
- **Intelligent Find Patterns**: Natural language find operations directly execute as OS commands.
- **Command Argument Support**: Over 100 command variations with common arguments.
- **Smart API Key Prompting**: API key prompted only for unknown commands; many commands available without setup.
- **Ambiguous Request Handling**: Addresses ambiguous patterns with multiple options and user preference learning.
- **Pattern Learning**: Intelligent command pattern learning from successful executions, directory tracking, and project type detection.

# External Dependencies

- **OpenAI API**: Used for natural language processing and command translation via GPT-4o.
- **Python Packages**:
    - `click`: For building the command-line interface.
    - `rich`: For enhanced console output and formatting.
    - `openai`: Official client for OpenAI API interaction.
    - `configparser`: For managing INI-based configuration files.
- **System Dependencies**:
    - Python 3.8+ runtime environment.
    - Standard Python library modules.
    - Operating system shell environments (bash, zsh, cmd, PowerShell).