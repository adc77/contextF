# contextF

Efficient context builder. Build relevant context from documents using configurable search patterns and token-aware windowing.

## Installation

```bash
pip install contextF
```

For PDF parsing:
```bash
pip install contextF[pdf]
```

## Quick Start

```python
from contextF import ContextBuilder

# Initialize with defaults
cb = ContextBuilder()

# Build context using direct patterns
result = cb.build_context(patterns=["machine learning", "neural networks"])

print(f"Context: {result['context']}")
print(f"Tokens: {result['context_tokens']}")
print(f"Files: {list(result['files_used'].keys())}")
```

## Configuration

### Basic Usage

```python
# Custom parameters
cb = ContextBuilder(
    docs_path="./my_docs",
    max_context_tokens=100000,
    context_window_tokens=5000
)
```

### JSON Configuration

```python
# Using config file
cb = ContextBuilder(config_path="config.json")
```

Example `config.json`:
```json
{
  "search": {
    "docs_path": "./documents",
    "max_patterns_per_query": 3,
    "max_matches_per_file": 5
  },
  "tokens": {
    "max_context_tokens": 200000,
    "context_window_tokens": 8000
  }
}
```

## Parameters

### Search Parameters
- `docs_path`: Directory containing documents (default: "./docs")
- `file_patterns`: File types to search (default: ["*.md", "*.txt"])
- `max_patterns_per_query`: Max search patterns to use (default: 3)
- `max_matches_per_file`: Max matches per file (default: 3)
- `case_sensitive`: Case sensitive search (default: false)

### Token Parameters
- `max_context_tokens`: Maximum total context tokens (default: 500000)
- `context_window_tokens`: Context window size around matches (default: 10000)
- `max_file_tokens`: Max tokens per file before windowing (default: 200000)
- `encoding`: Tokenizer encoding (default: "cl100k_base")

### LLM Parameters (Optional)
- `enabled`: Enable LLM pattern generation (default: true)
- `model`: OpenAI model (default: "gpt-4.1-mini")
- `temperature`: LLM temperature (default: 0.3)

## Pattern Generation

### Using LLM (requires OpenAI API key)
```python
# Set OPENAI_API_KEY environment variable
result = cb.build_context(query="how evaluation works in machine learning?")
```

### Direct Patterns
```python
# Bypass LLM, use direct patterns
result = cb.build_context(patterns=["evaluation", "machine learning", "algorithm"])
```

## Output Format

```python
{
    "context": "merged context text",
    "context_tokens": 15420,
    "files_used": {
        "file1.md": {
            "matches": 3,
            "tokens": 8500,
            "patterns_found": ["algorithm", "neural network"]
        }
    },
    "matches": {
        "file1.md": [
            {"line_num": 45, "text": "...", "pattern": "algorithm"}
        ]
    }
}
```

## Utilities

### PDF Parsing
```python
from contextF.utils import PDFParser

parser = PDFParser()
markdown_content = parser.convert_pdf_to_markdown("doc.pdf")
```

### Token Counting
```python
from contextF.utils import TokenCounter

counter = TokenCounter()
summary = counter.get_directory_summary("./docs")
print(f"Total tokens: {summary['total_tokens']}")
```

## Documentation
For detailed documentation, please refer to the [README.md](https://github.com/adc77/contextF/blob/main/README.md) file.