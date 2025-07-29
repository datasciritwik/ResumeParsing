from typing import Dict, Any
import os

class Config:
    """Configuration settings for the resume parser"""
    
    # NLP Model Configuration
    DEFAULT_SPACY_MODEL = "en_core_web_sm"
    FALLBACK_SPACY_MODEL = "en_core_web_md"  # More accurate but larger
    
    # PDF Processing Configuration
    USE_LAYOUT_ANALYSIS = True
    MAX_FILE_SIZE_MB = 10
    
    # Text Processing Configuration
    MIN_CONFIDENCE_SCORE = 0.7
    MAX_SKILL_LENGTH = 50
    MIN_SECTION_LENGTH = 10
    
    # Performance Configuration
    ENABLE_CACHING = True
    CACHE_TTL_SECONDS = 3600
    MAX_CONCURRENT_PROCESSES = 4
    
    # Output Configuration
    OUTPUT_FORMAT = "json"  # json, dict, pydantic
    INCLUDE_CONFIDENCE_SCORES = False
    INCLUDE_METADATA = True
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        return {
            'spacy_model': cls.DEFAULT_SPACY_MODEL,
            'use_layout_analysis': cls.USE_LAYOUT_ANALYSIS,
            'max_file_size_mb': cls.MAX_FILE_SIZE_MB,
            'min_confidence_score': cls.MIN_CONFIDENCE_SCORE,
            'enable_caching': cls.ENABLE_CACHING,
            'output_format': cls.OUTPUT_FORMAT,
            'include_metadata': cls.INCLUDE_METADATA,
            'log_level': cls.LOG_LEVEL
        }