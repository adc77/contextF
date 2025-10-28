from pathlib import Path
from typing import Optional, List
from ..exceptions import FileProcessingError

try:
    import pymupdf4llm
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

class PDFParser:
    """Utility class for converting PDF files to markdown"""
    
    def __init__(self):
        """Initialize PDF parser"""
        if not PYMUPDF_AVAILABLE:
            raise FileProcessingError(
                "pymupdf4llm is required for PDF parsing. Install with: pip install pymupdf4llm"
            )
    
    def convert_pdf_to_markdown(self, pdf_path: str, output_path: Optional[str] = None) -> str:
        """
        Convert a single PDF file to markdown
        
        Args:
            pdf_path: Path to PDF file
            output_path: Optional output path for markdown file
        
        Returns:
            Markdown content as string
        
        Raises:
            FileProcessingError: If conversion fails
        """
        try:
            pdf_file = Path(pdf_path)
            if not pdf_file.exists():
                raise FileProcessingError(f"PDF file not found: {pdf_path}")
            
            if not pdf_file.suffix.lower() == '.pdf':
                raise FileProcessingError(f"File is not a PDF: {pdf_path}")
            
            # Convert PDF to markdown
            markdown_content = pymupdf4llm.to_markdown(str(pdf_file))
            
            # Save to file if output path provided
            if output_path:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
            
            return markdown_content
            
        except Exception as e:
            if isinstance(e, FileProcessingError):
                raise
            raise FileProcessingError(f"Error converting PDF {pdf_path}: {e}")
    
    def convert_pdfs_to_markdown(self, 
                                input_folder: str, 
                                output_folder: str,
                                file_pattern: str = "*.pdf") -> List[str]:
        """
        Convert all PDF files in a folder to markdown files
        
        Args:
            input_folder: Path to folder containing PDF files
            output_folder: Path to folder where markdown files will be saved
            file_pattern: Pattern to match PDF files (default: "*.pdf")
        
        Returns:
            List of successfully converted file paths
        
        Raises:
            FileProcessingError: If conversion fails
        """
        try:
            input_path = Path(input_folder)
            output_path = Path(output_folder)
            
            if not input_path.exists():
                raise FileProcessingError(f"Input folder not found: {input_folder}")
            
            # Create output folder
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Get all PDF files
            pdf_files = list(input_path.glob(file_pattern))
            
            if not pdf_files:
                raise FileProcessingError(f"No PDF files found in {input_folder}")
            
            converted_files = []
            errors = []
            
            print(f"Found {len(pdf_files)} PDF file(s). Starting conversion...")
            
            for pdf_file in pdf_files:
                try:
                    print(f"Converting: {pdf_file.name}")
                    
                    # Convert to markdown
                    markdown_content = self.convert_pdf_to_markdown(str(pdf_file))
                    
                    # Save markdown file
                    output_file = output_path / f"{pdf_file.stem}.md"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(markdown_content)
                    
                    converted_files.append(str(output_file))
                    print(f"  -> Saved to: {output_file}")
                    
                except Exception as e:
                    error_msg = f"Error converting {pdf_file.name}: {e}"
                    errors.append(error_msg)
                    print(f"  -> {error_msg}")
            
            print(f"\nConversion complete. {len(converted_files)} files converted successfully.")
            
            if errors:
                print(f"Errors encountered:")
                for error in errors:
                    print(f"  - {error}")
            
            return converted_files
            
        except Exception as e:
            if isinstance(e, FileProcessingError):
                raise
            raise FileProcessingError(f"Error during batch PDF conversion: {e}")
    
    @staticmethod
    def is_available() -> bool:
        """
        Check if PDF parsing is available
        
        Returns:
            True if pymupdf4llm is available, False otherwise
        """
        return PYMUPDF_AVAILABLE
