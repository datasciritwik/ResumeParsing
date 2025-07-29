import fitz  # PyMuPDF
import pdfplumber
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class PDFExtractor:
    """Enhanced PDF text extraction with layout preservation"""
    
    def __init__(self, use_layout_analysis: bool = True):
        self.use_layout_analysis = use_layout_analysis
    
    def extract_text(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text with metadata and layout information"""
        try:
            result = {
                'text': '',
                'metadata': {},
                'layout_info': {}
            }
            
            # Primary extraction with PyMuPDF
            result['text'] = self._extract_with_pymupdf(pdf_path)
            
            # Enhanced extraction with pdfplumber for better layout
            if self.use_layout_analysis:
                layout_text, tables = self._extract_with_pdfplumber(pdf_path)
                if len(layout_text) > len(result['text']):
                    result['text'] = layout_text
                result['layout_info']['tables'] = tables
            
            # Extract metadata
            result['metadata'] = self._extract_metadata(pdf_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting PDF {pdf_path}: {str(e)}")
            raise
    
    def _extract_with_pymupdf(self, pdf_path: str) -> str:
        """Fast text extraction with PyMuPDF"""
        text = ""
        try:
            with fitz.open(pdf_path) as doc:
                for page_num, page in enumerate(doc):
                    # Extract text with layout preservation
                    page_text = page.get_text("text")
                    text += f"\n--- PAGE {page_num + 1} ---\n{page_text}"
        except Exception as e:
            logger.warning(f"PyMuPDF extraction failed: {str(e)}")
            
        return text
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> tuple:
        """Layout-aware text extraction with pdfplumber"""
        text = ""
        tables = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract text with better layout handling
                    page_text = page.extract_text(layout=True)
                    if page_text:
                        text += f"\n--- PAGE {page_num + 1} ---\n{page_text}"
                    
                    # Extract tables
                    page_tables = page.extract_tables()
                    if page_tables:
                        tables.extend([{
                            'page': page_num + 1,
                            'data': table
                        } for table in page_tables])
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {str(e)}")
            
        return text, tables
    
    def _extract_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """Extract PDF metadata"""
        metadata = {}
        try:
            with fitz.open(pdf_path) as doc:
                metadata = {
                    'page_count': doc.page_count,
                    'title': doc.metadata.get('title', ''),
                    'author': doc.metadata.get('author', ''),
                    'subject': doc.metadata.get('subject', ''),
                    'creator': doc.metadata.get('creator', ''),
                    'producer': doc.metadata.get('producer', ''),
                    'creation_date': doc.metadata.get('creationDate', ''),
                    'modification_date': doc.metadata.get('modDate', '')
                }
        except Exception as e:
            logger.warning(f"Metadata extraction failed: {str(e)}")
        
        return metadata