# Test Suite Organization

The test suite is organized to mirror the main source code structure, providing clear separation between different types of tests and making it easy to locate and run specific test categories.

## Directory Structure

```
tests/
├── pipeline/          # Tests for AI translation and command processing
├── execution/         # Tests for command execution and safety
├── storage/           # Tests for data persistence and caching
├── context/           # Tests for context intelligence features
├── ui/                # Tests for user interface components
├── cli/               # Tests for command-line interface
├── utils/             # Tests for utility functions
├── mocks/             # Mock tests for external dependencies
└── README.md          # This documentation
```

## Test Categories

### 📋 Pipeline Tests (`tests/pipeline/`)
Tests for natural language processing and command filtering:
- `test_ai_translator.py` - Core AI translation functionality
- `test_ai_translator_basic.py` - Basic AI translator tests
- `test_ai_translator_focused.py` - Focused realistic scenarios
- `test_command_filter.py` - Direct command recognition
- `test_pattern_engine.py` - Semantic pattern matching
- `test_fuzzy_engine.py` - Fuzzy matching algorithms
- `test_typo_corrector.py` - Typo detection and correction

### ⚡ Execution Tests (`tests/execution/`)
Tests for command execution and safety validation:
- `test_command_executor.py` - Command execution engine
- `test_command_executor_basic.py` - Basic execution tests
- `test_safety_checker.py` - Safety validation and dangerous command detection

### 💾 Storage Tests (`tests/storage/`)
Tests for data persistence and configuration:
- `test_cache_manager.py` - Cache system functionality
- `test_config_manager.py` - Configuration management
- `test_file_history.py` - File-based history storage

### 🧠 Context Tests (`tests/context/`)
Tests for intelligence and awareness features:
- Context manager tests
- Git repository awareness tests
- Environment detection tests

### 🎨 UI Tests (`tests/ui/`)
Tests for user interface components:
- Output formatter tests
- Interactive input tests

### 🖥️ CLI Tests (`tests/cli/`)
Tests for command-line interface:
- Main CLI entry point tests
- Subcommand tests

### 🔧 Utils Tests (`tests/utils/`)
Tests for utility functions:
- Platform detection tests
- Helper function tests

### 🧪 Mock Tests (`tests/mocks/`)
**Specialized tests for external API dependencies:**
- `test_ai_translator_mocks.py` - Pure OpenAI API mocking
- `test_ai_translator_integration.py` - Real component integration with mocked APIs
- `test_ai_translator_comprehensive.py` - Advanced API interaction testing

## Mock Testing Strategy

The `mocks/` directory contains tests specifically designed to handle external dependencies:

### Purpose
- Test functions that use external APIs (OpenAI GPT-4o)
- Simulate error conditions (rate limits, timeouts)
- Provide fast, reliable, cost-effective testing
- Enable offline development and testing

### Benefits
- **No API costs** during testing
- **Fast execution** (milliseconds vs seconds)
- **Predictable results** every time
- **Comprehensive error testing** for edge cases
- **Offline capability** for development

### Mock Types
1. **OpenAI API Mocking** - Fake API responses and error conditions
2. **Cache System Mocking** - Simulated cache hits/misses
3. **File System Mocking** - Isolated temporary environments
4. **Environment Mocking** - Controlled configuration testing

## Running Tests

### Run all tests:
```bash
python -m pytest tests/
```

### Run specific category:
```bash
python -m pytest tests/pipeline/
python -m pytest tests/mocks/
```

### Run specific test file:
```bash
python -m pytest tests/mocks/test_ai_translator_mocks.py
```

### Run with coverage:
```bash
python -m pytest tests/ --cov=nlcli
```

## Test Organization Benefits

1. **Clear Structure** - Easy to locate tests for specific components
2. **Separation of Concerns** - Mock tests isolated from unit tests
3. **Scalability** - Easy to add new tests in appropriate categories
4. **Maintainability** - Mirror source structure for intuitive navigation
5. **CI/CD Friendly** - Can run specific test categories in parallel

This organization ensures comprehensive test coverage while maintaining enterprise-grade testing standards and developer productivity.