import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from ..core.text_processor import TextProcessor
from ..core.config import ConfigManager
from ..exceptions import FileProcessingError

class TokenCounter:
    """Utility class for counting tokens in files and directories"""
    
    def __init__(self, encoding: str = "cl100k_base"):
        """
        Initialize token counter
        
        Args:
            encoding: Tokenizer encoding to use
        """
        # Create minimal config for text processor
        config = {
            'tokens': {
                'encoding': encoding,
                'context_window_tokens': 10000,
                'max_context_tokens': 500000,
                'max_file_tokens': 200000
            },
            'text_processing': {
                'chunk_size': 1000,
                'chunk_overlap': 200,
                'merge_overlapping_windows': True
            }
        }
        
        self.text_processor = TextProcessor(config)
    
    def count_tokens_in_file(self, file_path: str) -> int:
        """
        Count tokens in a single file
        
        Args:
            file_path: Path to file
        
        Returns:
            Number of tokens in the file
        
        Raises:
            FileProcessingError: If file cannot be read
        """
        try:
            file_obj = Path(file_path)
            if not file_obj.exists():
                raise FileProcessingError(f"File not found: {file_path}")
            
            with open(file_obj, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return self.text_processor.count_tokens(content)
            
        except Exception as e:
            if isinstance(e, FileProcessingError):
                raise
            raise FileProcessingError(f"Error counting tokens in {file_path}: {e}")
    
    def count_tokens_in_directory(self, 
                                 directory: str,
                                 file_patterns: Optional[List[str]] = None,
                                 recursive: bool = True) -> Dict[str, int]:
        """
        Count tokens in all matching files in a directory
        
        Args:
            directory: Path to directory
            file_patterns: List of file patterns to match (default: ['*.md', '*.txt'])
            recursive: Whether to search recursively
        
        Returns:
            Dictionary mapping file paths to token counts
        
        Raises:
            FileProcessingError: If directory cannot be accessed
        """
        if file_patterns is None:
            file_patterns = ['*.md', '*.txt']
        
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                raise FileProcessingError(f"Directory not found: {directory}")
            
            if not dir_path.is_dir():
                raise FileProcessingError(f"Path is not a directory: {directory}")
            
            file_token_counts = {}
            
            # Get all matching files
            for pattern in file_patterns:
                if recursive:
                    files = dir_path.rglob(pattern)
                else:
                    files = dir_path.glob(pattern)
                
                for file_path in files:
                    if file_path.is_file():
                        try:
                            token_count = self.count_tokens_in_file(str(file_path))
                            file_token_counts[str(file_path)] = token_count
                        except FileProcessingError as e:
                            print(f"Warning: {e}")
                            continue
            
            return file_token_counts
            
        except Exception as e:
            if isinstance(e, FileProcessingError):
                raise
            raise FileProcessingError(f"Error counting tokens in directory {directory}: {e}")
    
    def get_directory_summary(self, 
                            directory: str,
                            file_patterns: Optional[List[str]] = None,
                            recursive: bool = True) -> Dict[str, any]:
        """
        Get a summary of token counts for a directory
        
        Args:
            directory: Path to directory
            file_patterns: List of file patterns to match
            recursive: Whether to search recursively
        
        Returns:
            Dictionary containing summary statistics
        """
        try:
            file_counts = self.count_tokens_in_directory(directory, file_patterns, recursive)
            
            if not file_counts:
                return {
                    'total_files': 0,
                    'total_tokens': 0,
                    'average_tokens': 0,
                    'min_tokens': 0,
                    'max_tokens': 0,
                    'files': {}
                }
            
            total_tokens = sum(file_counts.values())
            token_values = list(file_counts.values())
            
            return {
                'total_files': len(file_counts),
                'total_tokens': total_tokens,
                'average_tokens': total_tokens // len(file_counts),
                'min_tokens': min(token_values),
                'max_tokens': max(token_values),
                'files': file_counts
            }
            
        except Exception as e:
            raise FileProcessingError(f"Error generating directory summary: {e}")
    
    def print_directory_report(self, 
                             directory: str,
                             file_patterns: Optional[List[str]] = None,
                             recursive: bool = True,
                             sort_by_tokens: bool = True):
        """
        Print a detailed report of token counts in a directory
        
        Args:
            directory: Path to directory
            file_patterns: List of file patterns to match
            recursive: Whether to search recursively
            sort_by_tokens: Whether to sort files by token count
        """
        try:
            summary = self.get_directory_summary(directory, file_patterns, recursive)
            
            print(f"Token Count Report for: {directory}")
            print("=" * 60)
            print(f"Total files: {summary['total_files']}")
            print(f"Total tokens: {summary['total_tokens']:,}")
            print(f"Average tokens per file: {summary['average_tokens']:,}")
            print(f"Min tokens: {summary['min_tokens']:,}")
            print(f"Max tokens: {summary['max_tokens']:,}")
            print("\nPer-file breakdown:")
            print("-" * 60)
            
            files = summary['files']
            if sort_by_tokens:
                files = dict(sorted(files.items(), key=lambda x: x[1], reverse=True))
            
            for file_path, token_count in files.items():
                filename = Path(file_path).name
                print(f"{filename:<40} {token_count:>10,} tokens")
            
        except Exception as e:
            print(f"Error generating report: {e}")
    
    def count_tokens_in_text(self, text: str) -> int:
        """
        Count tokens in a text string
        
        Args:
            text: Text to count tokens for
        
        Returns:
            Number of tokens
        """
        return self.text_processor.count_tokens(text)
