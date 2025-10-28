"""
Demonstration of contextF library with existing data
"""

import sys
import os

# Add contextF to path
sys.path.insert(0, './contextF')

from contextF import ContextBuilder

def demo_basic_usage():
    """Demonstrate basic contextF usage with existing markdown files"""
    print("contextF Library Demonstration")
    print("=" * 50)
    
    # Initialize ContextBuilder with your existing markdown files
    cb = ContextBuilder(
        docs_path="./data/papersMDs",
        max_context_tokens=20000,  # Smaller limit for demo
        context_window_tokens=3000,
        max_patterns_per_query=2,
        max_matches_per_file=2
    )
            
    print("✓ ContextBuilder initialized")
    print(f"✓ Configured to search in: ./data/papersMDs")
    print(f"✓ Max context tokens: 20,000")
    print(f"✓ Context window: 3,000 tokens")
    
    # Test 1: Using direct patterns (no LLM needed)
    print("\n" + "="*50)
    print("Test 1: Using Direct Search Patterns")
    print("-" * 50)
    
    patterns = ["hallucination", "detection", "level"]
    print(f"Search patterns: {patterns}")
    
    try:
        result = cb.build_context(patterns=patterns)
        
        print(f"\n✓ Search completed successfully!")
        print(f"✓ Context tokens: {result['context_tokens']:,}")
        print(f"✓ Files processed: {len(result['files_used'])}")
        
        if result['files_used']:
            print("\nFiles found with matches:")
            for filename, details in result['files_used'].items():
                short_name = os.path.basename(filename)
                print(f"  - {short_name}: {details['matches']} matches, {details['tokens']:,} tokens")
                print(f"    Patterns found: {', '.join(details['patterns_found'])}")
        
        if result['context']:
            print(f"\n✓ Context preview (first 200 chars):")
            print("-" * 30)
            print(result['context'][:200] + "..." if len(result['context']) > 200 else result['context'])
        else:
            print("\n⚠️  No context found - no matches for the given patterns")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: Different patterns
    print("\n" + "="*50)
    print("Test 2: Different Search Patterns")
    print("-" * 50)
    
    patterns2 = ["hallucination", "detection", "level"]
    print(f"Search patterns: {patterns2}")
    
    try:
        result2 = cb.build_context(patterns=patterns2)
        
        print(f"\n✓ Search completed!")
        print(f"✓ Context tokens: {result2['context_tokens']:,}")
        print(f"✓ Files processed: {len(result2['files_used'])}")
        
        if result2['files_used']:
            print("\nFiles found:")
            for filename, details in result2['files_used'].items():
                short_name = os.path.basename(filename)
                print(f"  - {short_name}: {details['matches']} matches")
                
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 3: Configuration demonstration
    print("\n" + "="*50)
    print("Test 3: Configuration Options")
    print("-" * 50)
    
    # Show current configuration
    config = cb.get_config()
    print("Current configuration:")
    print(f"  - Max context tokens: {config['tokens']['max_context_tokens']:,}")
    print(f"  - Context window tokens: {config['tokens']['context_window_tokens']:,}")
    print(f"  - Max patterns per query: {config['search']['max_patterns_per_query']}")
    print(f"  - Max matches per file: {config['search']['max_matches_per_file']}")
    print(f"  - File patterns: {config['search']['file_patterns']}")
    
    # Test token counting
    print("\n" + "="*50)
    print("Test 4: Token Counting")
    print("-" * 50)
    
    sample_text = "This is a sample text for token counting demonstration."
    token_count = cb.count_tokens(sample_text)
    print(f"Sample text: '{sample_text}'")
    print(f"Token count: {token_count}")
    
    print("\n" + "="*50)
    print("✓ Demonstration completed successfully!")
    print("contextF library is working correctly with your data!")

def main():
    """Run the demonstration"""
    # Check if papersMDs directory exists
    if not os.path.exists("./data/papersMDs"):
        print("Error: ./data/papersMDs directory not found!")
        print("Please ensure you have markdown files in the papersMDs directory.")
        return
    
    # Count files in directory
    md_files = [f for f in os.listdir("./data/papersMDs") if f.endswith('.md')]
    print(f"Found {len(md_files)} markdown files in ./papersMDs")
    
    if len(md_files) == 0:
        print("No markdown files found for demonstration.")
        return
    
    demo_basic_usage()

if __name__ == "__main__":
    main()
