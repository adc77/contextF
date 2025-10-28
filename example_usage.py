"""
Example usage of contextF library
"""

from json import load
import os
from contextF import ContextBuilder
from contextF.utils import PDFParser, TokenCounter
from dotenv import load_dotenv
load_dotenv()

def main():
    """Demonstrate contextF library usage"""
    
    print("contextF Library Example Usage")
    print("=" * 50)
    
    # Example 1: Basic usage with query
    print("\n1. Basic Usage with Query")
    print("-" * 30)
    
    cb = ContextBuilder(
        docs_path="data\papersMDs",  # Adjust path as needed
        max_context_tokens=50000,
        context_window_tokens=5000,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    query = "how to implement hallucination detection at model level in LLMs?"
    result = cb.build_context(query=query)
    
    print(f"Query: {query}")
    print(f"Context tokens: {result['context_tokens']}")
    print(f"Files used: {len(result['files_used'])}")
    
    if result['files_used']:
        print("Files processed:")
        for filename, details in result['files_used'].items():
            print(f"  - {filename}: {details['matches']} matches, {details['tokens']} tokens")
    
    # Example 2: Using direct patterns
    print("\n2. Using Direct Patterns")
    print("-" * 30)
    
    patterns = ["hallucination", "detection", "level"]
    result = cb.build_context(patterns=patterns)
    
    print(f"Patterns: {patterns}")
    print(f"Context tokens: {result['context_tokens']}")
    print(f"Files used: {len(result['files_used'])}")
    
    # Example 3: Custom configuration
    print("\n3. Custom Configuration")
    print("-" * 30)
    
    cb_custom = ContextBuilder( 
        docs_path="data\papersMDs",
        max_context_tokens=100000,
        context_window_tokens=8000,
        max_patterns_per_query=5,
        max_matches_per_file=5
    )
    
    result = cb_custom.build_context(query="hallucination deetction at model level")
    print(f"Custom config - Context tokens: {result['context_tokens']}")
    
    # Example 4: Token counting utility
    print("\n4. Token Counting Utility")
    print("-" * 30)
    
    counter = TokenCounter()
    
    # Check if directory exists
    if os.path.exists("data\papersMDs"):
        summary = counter.get_directory_summary("data\papersMDs", ["*.md"])
        print(f"Directory: data\papersMDs")
        print(f"Total files: {summary['total_files']}")
        print(f"Total tokens: {summary['total_tokens']:,}")
        print(f"Average tokens per file: {summary['average_tokens']:,}")
    else:
        print("Directory data\papersMDs not found - skipping token counting example")
    
    # Example 5: PDF parsing (if available)
    print("\n5. PDF Parsing Utility")
    print("-" * 30)
    
    if PDFParser.is_available():
        print("PDF parsing is available")
        # Uncomment to test PDF parsing:
        # parser = PDFParser()
        # if os.path.exists("./papersPDF"):
        #     converted = parser.convert_pdfs_to_markdown("./papersPDF", "./converted_mds")
        #     print(f"Converted {len(converted)} PDF files")
    else:
        print("PDF parsing not available - install with: pip install pymupdf4llm")
    
    # Example 6: Configuration from file
    print("\n6. Configuration from File")
    print("-" * 30)
    
    # Create example config file
    config_content = """{
  "search": {
    "docs_path": "data\papersMDs",
    "max_patterns_per_query": 4,
    "max_matches_per_file": 4
  },
  "tokens": {
    "max_context_tokens": 75000,
    "context_window_tokens": 6000
  },
  "llm": {
    "enabled": true,
    "model": "gpt-4.1-mini",
    "temperature": 0.2
  }
}"""
    
    with open("example_config.json", "w") as f:
        f.write(config_content)
    
    try:
        cb_config = ContextBuilder(config_path="example_config.json")
        result = cb_config.build_context(query="hallucination deetction at model level")
        print(f"Config file - Context tokens: {result['context_tokens']}")
    except Exception as e:
        print(f"Config file example failed: {e}")
    finally:
        # Clean up
        if os.path.exists("example_config.json"):
            os.remove("example_config.json")
    
    print("\nExample usage complete!")

if __name__ == "__main__":
    main()
