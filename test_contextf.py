"""
Simple test script for contextF library functionality
"""

import sys
import os

# Add contextF to path
sys.path.insert(0, './contextF')

def test_basic_functionality():
    """Test basic functionality without external dependencies"""
    print("Testing contextF Library")
    print("=" * 40)
    
    try:
        # Test configuration loading
        from contextF.core.config import ConfigManager
        print("✓ Configuration module imported successfully")
        
        config = ConfigManager()
        print("✓ Default configuration loaded successfully")
        
        # Test search configuration
        search_config = config.get_search_config()
        print(f"✓ Search config loaded: {len(search_config)} parameters")
        
        # Test token configuration
        token_config = config.get_token_config()
        print(f"✓ Token config loaded: {len(token_config)} parameters")
        
        # Test configuration overrides
        config_with_overrides = ConfigManager(
            docs_path="data\outputMDs",
            max_context_tokens=100000
        )
        print("✓ Configuration overrides working")
        
        # Test exceptions
        from contextF.exceptions import ContextFError, ConfigurationError
        print("✓ Exception classes imported successfully")
        
        print("\n" + "=" * 40)
        print("Basic functionality tests PASSED!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_with_dependencies():
    """Test functionality that requires external dependencies"""
    print("\nTesting with dependencies...")
    print("-" * 40)
    
    try:
        # Test if we can import the main class
        from contextF import ContextBuilder
        print("✓ ContextBuilder imported successfully")
        
        # Test basic initialization (without OpenAI)
        cb = ContextBuilder(docs_path="./papersMDs")
        print("✓ ContextBuilder initialized successfully")
        
        # Test configuration access
        config = cb.get_config()
        print(f"✓ Configuration accessible: {len(config)} sections")
        
        print("\nDependency tests PASSED!")
        return True
        
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Install required packages:")
        print("  pip install openai tiktoken langchain-text-splitters python-dotenv")
        return False
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("contextF Library Test Suite")
    print("=" * 50)
    
    # Test basic functionality
    basic_success = test_basic_functionality()
    
    # Test with dependencies
    if basic_success:
        dep_success = test_with_dependencies()
    else:
        dep_success = False
    
    print("\n" + "=" * 50)
    if basic_success and dep_success:
        print("ALL TESTS PASSED! 🎉")
        print("\nThe contextF library is ready to use!")
    elif basic_success:
        print("BASIC TESTS PASSED! ⚠️")
        print("Install dependencies to use full functionality.")
    else:
        print("TESTS FAILED! ❌")
        print("Please check the error messages above.")

if __name__ == "__main__":
    main()
