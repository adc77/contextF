import tiktoken
from typing import List, Dict, Any, Tuple
from ..exceptions import TokenLimitError, FileProcessingError

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    # Simple fallback text splitter
    class RecursiveCharacterTextSplitter:
        def __init__(self, chunk_size=1000, chunk_overlap=200, length_function=None):
            self.chunk_size = chunk_size
            self.chunk_overlap = chunk_overlap
            self.length_function = length_function or len

class TextProcessor:
    """Handles text processing, tokenization, and context windowing"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize text processor
        
        Args:
            config: Configuration dictionary containing token and text processing settings
        """
        self.token_config = config['tokens']
        self.text_config = config['text_processing']
        
        # Initialize tokenizer
        encoding_name = self.token_config.get('encoding', 'cl100k_base')
        try:
            self.tokenizer = tiktoken.get_encoding(encoding_name)
        except Exception as e:
            raise FileProcessingError(f"Failed to initialize tokenizer with encoding '{encoding_name}': {e}")
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.text_config.get('chunk_size', 1000),
            chunk_overlap=self.text_config.get('chunk_overlap', 200),
            length_function=self.count_tokens
        )
        
        # Configuration values
        self.context_window_tokens = self.token_config['context_window_tokens']
        self.max_context_tokens = self.token_config['max_context_tokens']
        self.max_file_tokens = self.token_config['max_file_tokens']
        self.merge_overlapping = self.text_config.get('merge_overlapping_windows', True)
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using tiktoken
        
        Args:
            text: Text to count tokens for
        
        Returns:
            Number of tokens
        """
        try:
            return len(self.tokenizer.encode(text))
        except Exception as e:
            raise FileProcessingError(f"Error counting tokens: {e}")
    
    def extract_context_window(self, text: str, line_num: int) -> Tuple[str, int, int]:
        """
        Extract context window around a specific line
        
        Args:
            text: Full text content
            line_num: Line number to center the window around
        
        Returns:
            Tuple of (context_text, start_line, end_line)
        """
        try:
            lines = text.split('\n')
            total_lines = len(lines)
            
            if line_num > total_lines:
                line_num = total_lines
            
            # Estimate tokens per line
            total_tokens = self.count_tokens(text)
            tokens_per_line_approx = total_tokens / total_lines if total_lines > 0 else 0
            
            # Calculate lines needed for context window
            if tokens_per_line_approx > 0:
                lines_for_window = int(self.context_window_tokens / tokens_per_line_approx)
            else:
                lines_for_window = 50  # Default fallback
            
            # Calculate window boundaries
            start_line = max(0, line_num - lines_for_window - 1)
            end_line = min(total_lines, line_num + lines_for_window)
            
            context_text = '\n'.join(lines[start_line:end_line])
            
            return context_text, start_line, end_line
            
        except Exception as e:
            raise FileProcessingError(f"Error extracting context window: {e}")
    
    def merge_overlapping_windows(self, windows: List[Dict[str, Any]]) -> str:
        """
        Merge overlapping context windows
        
        Args:
            windows: List of window dictionaries with 'text', 'start_line', 'end_line'
        
        Returns:
            Merged context text
        """
        if not windows:
            return ""
        
        try:
            # Sort windows by start line
            sorted_windows = sorted(windows, key=lambda x: x['start_line'])
            merged = [sorted_windows[0]]
            
            for current in sorted_windows[1:]:
                last = merged[-1]
                
                # Check for overlap
                if current['start_line'] <= last['end_line']:
                    # Merge overlapping windows
                    last['end_line'] = max(last['end_line'], current['end_line'])
                    # Combine text (avoiding duplication)
                    if current['text'] not in last['text']:
                        last['text'] = last['text'] + '\n' + current['text']
                else:
                    # No overlap, add as separate window
                    merged.append(current)
            
            return '\n\n'.join([w['text'] for w in merged])
            
        except Exception as e:
            raise FileProcessingError(f"Error merging context windows: {e}")
    
    def process_file_content(self, filename: str, matches: List[Dict[str, Any]]) -> Tuple[str, int]:
        """
        Process file content and extract relevant context
        
        Args:
            filename: Path to file
            matches: List of match dictionaries
        
        Returns:
            Tuple of (context_text, token_count)
        """
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                return "", 0
            
            file_tokens = self.count_tokens(content)
            
            # If file is small enough, return entire content
            if file_tokens <= self.max_file_tokens:
                return content, file_tokens
            
            # For large files, extract context windows around matches
            if not matches:
                return "", 0
            
            windows = []
            for match in matches:
                window_text, start_line, end_line = self.extract_context_window(
                    content, match['line_num']
                )
                windows.append({
                    'text': window_text,
                    'start_line': start_line,
                    'end_line': end_line
                })
            
            # Merge overlapping windows if configured
            if self.merge_overlapping:
                merged_context = self.merge_overlapping_windows(windows)
            else:
                merged_context = '\n\n'.join([w['text'] for w in windows])
            
            context_tokens = self.count_tokens(merged_context)
            
            return merged_context, context_tokens
            
        except Exception as e:
            raise FileProcessingError(f"Error processing file {filename}: {e}")
    
    def validate_token_limits(self, context_tokens: int):
        """
        Validate that token limits are not exceeded
        
        Args:
            context_tokens: Number of context tokens
        
        Raises:
            TokenLimitError: If token limits are exceeded
        """
        if context_tokens > self.max_context_tokens:
            raise TokenLimitError(
                f"Context tokens ({context_tokens}) exceed maximum limit ({self.max_context_tokens})"
            )
