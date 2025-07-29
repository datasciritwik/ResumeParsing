import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path
import json
import time
from functools import lru_cache

from ..extractors.pdf_extractor import PDFExtractor
from ..extractors.text_cleaner import TextCleaner
from ..extractors.entity_extractor import EntityExtractor
from ..models.schemas import ResumeData
from .config import Config

# Setup logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

class ResumeParser:
    """High-performance resume parser with caching and error handling"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize parser with optional custom configuration"""
        self.config = Config.get_config()
        if config:
            self.config.update(config)
        
        # Initialize components
        self.pdf_extractor = PDFExtractor(
            use_layout_analysis=self.config['use_layout_analysis']
        )
        self.text_cleaner = TextCleaner()
        self.entity_extractor = EntityExtractor(
            model_name=self.config['spacy_model']
        )
        
        logger.info("ResumeParser initialized successfully")
    
    def parse(self, pdf_path: Union[str, Path]) -> Union[Dict[str, Any], ResumeData, str]:
        """
        Main parsing method
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Parsed resume data in specified format
        """
        start_time = time.time()
        pdf_path = Path(pdf_path)
        
        try:
            # Validate input
            self._validate_input(pdf_path)
            
            # Check cache if enabled
            if self.config['enable_caching']:
                cached_result = self._get_cached_result(pdf_path)
                if cached_result:
                    logger.info(f"Returning cached result for {pdf_path.name}")
                    return cached_result
            
            # Extract text from PDF
            logger.info(f"Starting PDF extraction for {pdf_path.name}")
            pdf_data = self.pdf_extractor.extract_text(str(pdf_path))
            
            # Clean and preprocess text
            logger.info("Cleaning and preprocessing text")
            cleaned_text = self.text_cleaner.clean(pdf_data['text'])
            # print(cleaned_text)  # DEBUG
            sections = self.text_cleaner.extract_sections(cleaned_text)
            # print("sections", sections)
            # Extract entities
            logger.info("Extracting entities")
            resume_data = self.entity_extractor.extract_entities(cleaned_text, sections)
            
            # Add metadata if requested
            if self.config['include_metadata']:
                result = {
                    'resume_data': resume_data,
                    'metadata': {
                        **pdf_data['metadata'],
                        'processing_time': time.time() - start_time,
                        'parser_version': '1.0.0',
                        'sections_found': list(sections.keys())
                    }
                }
            else:
                result = resume_data
            
            # Cache result if enabled
            if self.config['enable_caching']:
                self._cache_result(pdf_path, result)
            
            # Format output
            formatted_result = self._format_output(result)
            
            logger.info(f"Successfully parsed {pdf_path.name} in {time.time() - start_time:.2f}s")
            return formatted_result
            
        except Exception as e:
            logger.error(f"Error parsing {pdf_path}: {str(e)}")
            raise
    
    def parse_batch(self, pdf_paths: list) -> Dict[str, Any]:
        """Parse multiple resumes in batch"""
        results = {}
        errors = {}
        
        logger.info(f"Starting batch processing of {len(pdf_paths)} files")
        
        for pdf_path in pdf_paths:
            try:
                results[str(pdf_path)] = self.parse(pdf_path)
            except Exception as e:
                errors[str(pdf_path)] = str(e)
                logger.error(f"Failed to parse {pdf_path}: {str(e)}")
        
        return {
            'results': results,
            'errors': errors,
            'summary': {
                'total_files': len(pdf_paths),
                'successful': len(results),
                'failed': len(errors)
            }
        }
    
    def _validate_input(self, pdf_path: Path):
        """Validate input file"""
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if pdf_path.suffix.lower() != '.pdf':
            raise ValueError(f"File must be a PDF: {pdf_path}")
        
        # Check file size
        file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.config['max_file_size_mb']:
            raise ValueError(f"File too large: {file_size_mb:.1f}MB > {self.config['max_file_size_mb']}MB")
    
    @lru_cache(maxsize=100)
    def _get_cached_result(self, pdf_path: Path) -> Optional[Any]:
        """Get cached result (simple in-memory cache)"""
        # In production, you might want to use Redis or disk cache
        return None
    
    def _cache_result(self, pdf_path: Path, result: Any):
        """Cache parsing result"""
        # Implementation depends on caching strategy
        pass
    
    def _format_output(self, result: Any) -> Any:
        """Format output according to configuration"""
        if self.config['output_format'] == 'json':
            if isinstance(result, ResumeData):
                return result.json(indent=2)
            else:
                return json.dumps(result, indent=2, default=str)
        elif self.config['output_format'] == 'dict':
            if isinstance(result, ResumeData):
                return result.dict()
            return result
        else:  # pydantic
            return result
    
    def get_supported_formats(self) -> list:
        """Get list of supported file formats"""
        return ['.pdf']
    
    def get_parser_info(self) -> Dict[str, Any]:
        """Get parser information and statistics"""
        return {
            'version': '1.0.0',
            'supported_formats': self.get_supported_formats(),
            'configuration': self.config,
            'components': {
                'pdf_extractor': 'PyMuPDF + pdfplumber',
                'nlp_model': self.config['spacy_model'],
                'skills_database': 'Enhanced with 200+ skills',
                'text_cleaner': 'Advanced preprocessing'
            }
        }