import os
from typing import List, Dict, Any, Optional, Union, Tuple
from .core.config import ConfigManager
from .core.search import SearchEngine
from .core.text_processor import TextProcessor
from .exceptions import ContextFError, ConfigurationError, SearchError
from dotenv import load_dotenv
load_dotenv()
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

class ContextBuilder:
    """
    Main class for building context from documents using configurable search patterns
    """
    
    def __init__(self, 
                 config_path: Optional[str] = None,
                 openai_api_key: Optional[str] = None,
                 **config_overrides):
        """
        Initialize ContextBuilder
        
        Args:
            config_path: Path to JSON configuration file
            openai_api_key: OpenAI API key for LLM pattern generation
            **config_overrides: Configuration overrides as keyword arguments
        
        Example:
            # Using defaults
            cb = ContextBuilder()
            
            # With config file
            cb = ContextBuilder(config_path="my_config.json")
            
            # With overrides
            cb = ContextBuilder(
                docs_path="./my_docs",
                max_context_tokens=100000,
                context_window_tokens=5000
            )
        """
        # Initialize configuration
        self.config_manager = ConfigManager(config_path, **config_overrides)
        
        # Initialize components
        self.search_engine = SearchEngine(self.config_manager.get_search_config())
        self.text_processor = TextProcessor({
            'tokens': self.config_manager.get_token_config(),
            'text_processing': self.config_manager.get_text_processing_config()
        })
        
        # Initialize OpenAI client if API key provided and LLM enabled
        self.openai_client = None
        llm_config = self.config_manager.get_llm_config()
        
        if llm_config.get('enabled', True) and OPENAI_AVAILABLE:
            api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
            if api_key:
                try:
                    self.openai_client = OpenAI(api_key=api_key)
                except Exception as e:
                    raise ConfigurationError(f"Failed to initialize OpenAI client: {e}")
        elif llm_config.get('enabled', True) and not OPENAI_AVAILABLE:
            print("Warning: OpenAI not available. Install with: pip install openai")
    
    def generate_search_patterns(self, query: str) -> List[str]:
        """
        Generate search patterns using LLM or return query as single pattern
        
        Args:
            query: Search query
        
        Returns:
            List of search patterns
        """
        llm_config = self.config_manager.get_llm_config()
        max_patterns = self.config_manager.get('search.max_patterns_per_query', 3)
        
        if not llm_config.get('enabled', True) or not self.openai_client:
            # Fallback to using query as pattern
            return [query.strip()]
        
        try:
            prompt_template = llm_config.get('pattern_generation_prompt', 
                "Generate search patterns for: {query}")
            prompt = prompt_template.format(query=query, max_patterns=max_patterns)
            
            response = self.openai_client.chat.completions.create(
                model=llm_config.get('model', 'gpt-4.1-mini'),
                messages=[{"role": "user", "content": prompt}],
                temperature=llm_config.get('temperature', 0.3)
            )
            
            patterns = response.choices[0].message.content.strip().split('\n')
            patterns = [p.strip() for p in patterns if p.strip()][:max_patterns]
            
            return patterns if patterns else [query.strip()]
            
        except Exception as e:
            # Fallback to query if LLM fails
            print(f"Warning: LLM pattern generation failed, using query as pattern: {e}")
            return [query.strip()]
    
    def build_context(self, 
                     query: Optional[str] = None, 
                     patterns: Optional[List[str]] = None,
                     docs_path: Optional[str] = None,
                     file_patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Build context from documents using search patterns
        
        Args:
            query: Search query (used for LLM pattern generation if patterns not provided)
            patterns: Direct search patterns (bypasses LLM generation)
            docs_path: Path to documents directory (overrides config)
            file_patterns: File patterns to search (overrides config)
        
        Returns:
            Dictionary containing:
            - context: Merged context text
            - context_tokens: Total number of tokens in context
            - files_used: Dictionary of files and their details
            - matches: Dictionary of all matches found
        
        Raises:
            ContextFError: If neither query nor patterns provided
            SearchError: If search fails
        """
        # Validate inputs
        if not query and not patterns:
            raise ContextFError("Either 'query' or 'patterns' must be provided")
        
        # Use provided patterns or generate from query
        if patterns:
            search_patterns = patterns[:self.config_manager.get('search.max_patterns_per_query', 3)]
        else:
            search_patterns = self.generate_search_patterns(query)
        
        # Get search configuration
        search_config = self.config_manager.get_search_config()
        docs_path = docs_path or search_config['docs_path']
        file_patterns = file_patterns or search_config['file_patterns']
        
        print(f"Search patterns: {search_patterns}")
        print(f"Searching in: {docs_path}")
        print(f"File patterns: {file_patterns}")
        
        try:
            # Search for patterns in files
            all_file_matches = self.search_engine.search_files(
                search_patterns, docs_path, file_patterns
            )
            
            if not all_file_matches:
                return {
                    "context": "",
                    "context_tokens": 0,
                    "files_used": {},
                    "matches": {}
                }
            
            print(f"Found matches in {len(all_file_matches)} file(s)")
            
            # Sort files by number of matches (prioritize files with more matches)
            sorted_files = sorted(
                all_file_matches.items(),
                key=lambda x: len(x[1]),
                reverse=True
            )
            
            # Process files and build context
            context_parts = []
            total_context_tokens = 0
            files_used = {}
            max_context_tokens = self.config_manager.get('tokens.max_context_tokens')
            
            for filename, matches in sorted_files:
                if total_context_tokens >= max_context_tokens:
                    print(f"Reached maximum context limit ({max_context_tokens} tokens)")
                    break
                
                print(f"Processing: {filename} ({len(matches)} matches)")
                
                # Filter unique matches
                unique_matches = self.search_engine.filter_unique_matches(matches)
                
                # Process file content
                file_context, file_tokens = self.text_processor.process_file_content(
                    filename, unique_matches
                )
                
                # Add to context if within limits
                if file_context and (total_context_tokens + file_tokens <= max_context_tokens):
                    context_parts.append(f"--- File: {filename} ---\n{file_context}")
                    total_context_tokens += file_tokens
                    
                    files_used[filename] = {
                        'matches': len(unique_matches),
                        'tokens': file_tokens,
                        'patterns_found': list(set(match['pattern'] for match in unique_matches))
                    }
            
            # Merge all context parts
            final_context = "\n\n".join(context_parts)
            
            # Validate token limits
            self.text_processor.validate_token_limits(total_context_tokens)
            
            return {
                "context": final_context,
                "context_tokens": total_context_tokens,
                "files_used": files_used,
                "matches": all_file_matches
            }
            
        except Exception as e:
            if isinstance(e, (ContextFError, SearchError)):
                raise
            raise ContextFError(f"Error building context: {e}")
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get current configuration
        
        Returns:
            Current configuration dictionary
        """
        return self.config_manager.config
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text
        
        Args:
            text: Text to count tokens for
        
        Returns:
            Number of tokens
        """
        return self.text_processor.count_tokens(text)
