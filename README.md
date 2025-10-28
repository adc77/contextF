# contextF - Efficient Context Builder

A Python library for building relevant context from documents using configurable search patterns and token-aware context windowing.

## Features

- **Flexible Pattern Matching**: Use LLM-generated patterns or provide your own search terms
- **Token-Aware Processing**: Intelligent context windowing based on token limits
- **Configurable Parameters**: Extensive configuration options via JSON files or class parameters
- **Multiple File Formats**: Support for Markdown (.md) and text (.txt) files
- **Optional Utilities**: PDF parsing and token counting utilities
- **Robust Error Handling**: Comprehensive error handling for production use

## Installation

```bash
pip install contextF
```

For PDF parsing capabilities:
```bash
pip install contextF[pdf]
```

## Quick Start

### Basic Usage

```python
from contextF import ContextBuilder

# Initialize with defaults
cb = ContextBuilder()

# Build context using a query (LLM will generate search patterns)
result = cb.build_context(query="machine learning algorithms")

print(f"Context: {result['context']}")
print(f"Tokens: {result['context_tokens']}")
print(f"Files used: {list(result['files_used'].keys())}")
```

### Using Direct Patterns

```python
# Bypass LLM and use direct search patterns
result = cb.build_context(patterns=["neural networks", "deep learning", "CNN"])
```

### Custom Configuration

```python
# Override specific parameters
cb = ContextBuilder(
    docs_path="./my_documents",
    max_context_tokens=100000,
    context_window_tokens=5000,
    max_patterns_per_query=5
)
```

### Using Configuration File

Create a `config.json` file:
```json
{
  "search": {
    "docs_path": "./documents",
    "file_patterns": ["*.md", "*.txt"],
    "max_patterns_per_query": 3,
    "max_matches_per_file": 5
  },
  "tokens": {
    "max_context_tokens": 200000,
    "context_window_tokens": 8000
  }
}
```

```python
cb = ContextBuilder(config_path="config.json")
```

## Configuration Options

### Search Configuration
- `docs_path`: Directory containing documents
- `file_patterns`: List of file patterns to search (e.g., `["*.md", "*.txt"]`)
- `max_patterns_per_query`: Maximum search patterns to generate/use
- `max_matches_per_file`: Maximum matches to consider per file
- `case_sensitive`: Whether search is case sensitive

### Token Configuration
- `context_window_tokens`: Size of context window around matches
- `max_context_tokens`: Maximum total context tokens
- `max_file_tokens`: Maximum tokens per file before windowing
- `encoding`: Tokenizer encoding (default: "cl100k_base")

### LLM Configuration
- `enabled`: Enable/disable LLM pattern generation
- `model`: OpenAI model to use (default: "gpt-4.1-mini")
- `temperature`: LLM temperature for pattern generation

## Optional Utilities

### PDF Parsing

```python
from contextF.utils import PDFParser

parser = PDFParser()

# Convert single PDF
markdown_content = parser.convert_pdf_to_markdown("document.pdf", "output.md")

# Convert all PDFs in a folder
converted_files = parser.convert_pdfs_to_markdown("./pdfs", "./markdown")
```

### Token Counting

```python
from contextF.utils import TokenCounter

counter = TokenCounter()

# Count tokens in a file
tokens = counter.count_tokens_in_file("document.md")

# Get directory summary
summary = counter.get_directory_summary("./documents")
print(f"Total tokens: {summary['total_tokens']}")

# Print detailed report
counter.print_directory_report("./documents")
```

## API Reference

### ContextBuilder

#### Methods

- `build_context(query=None, patterns=None, docs_path=None, file_patterns=None)`: Build context from documents
- `generate_search_patterns(query)`: Generate search patterns using LLM
- `count_tokens(text)`: Count tokens in text
- `get_config()`: Get current configuration

#### Returns

The `build_context` method returns a dictionary with:
- `context`: Merged context text
- `context_tokens`: Total number of tokens
- `files_used`: Dictionary of files and their details
- `matches`: Dictionary of all matches found

## Error Handling

contextF provides specific exception types:
- `ContextFError`: Base exception
- `ConfigurationError`: Configuration-related errors
- `SearchError`: Search operation errors
- `FileProcessingError`: File processing errors
- `TokenLimitError`: Token limit exceeded errors

## Requirements

- openai
- tiktoken
- langchain-text-splitters
- python-dotenv

Optional:
- pymupdf4llm (for PDF parsing)

## License

MIT License - see LICENSE file for details.