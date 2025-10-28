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

## Documentation
For detailed documentation and code examples, please refer to the [README.md](https://github.com/adc77/contextF/blob/main/README.md) file.