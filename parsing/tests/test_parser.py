import unittest
from pathlib import Path
import tempfile
import json

from ..core.parser import ResumeParser
from ..models.schemas import ResumeData

class TestResumeParser(unittest.TestCase):
    """Test cases for ResumeParser"""
    
    def setUp(self):
        """Set up test environment"""
        self.parser = ResumeParser()
        
    def test_parser_initialization(self):
        """Test parser initializes correctly"""
        self.assertIsInstance(self.parser, ResumeParser)
        self.assertIsNotNone(self.parser.pdf_extractor)
        self.assertIsNotNone(self.parser.text_cleaner)
        self.assertIsNotNone(self.parser.entity_extractor)
    
    def test_get_parser_info(self):
        """Test parser info method"""
        info = self.parser.get_parser_info()
        self.assertIn('version', info)
        self.assertIn('supported_formats', info)
        self.assertIn('configuration', info)
    
    def test_supported_formats(self):
        """Test supported formats"""
        formats = self.parser.get_supported_formats()
        self.assertIn('.pdf', formats)
    
    def test_invalid_file_validation(self):
        """Test validation of invalid files"""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse('nonexistent.pdf')
        
        # Create temporary non-PDF file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp.write(b'test content')
            tmp_path = tmp.name
        
        try:
            with self.assertRaises(ValueError):
                self.parser.parse(tmp_path)
        finally:
            Path(tmp_path).unlink()
    
    def test_batch_processing_empty_list(self):
        """Test batch processing with empty list"""
        results = self.parser.parse_batch([])
        self.assertEqual(results['summary']['total_files'], 0)
        self.assertEqual(results['summary']['successful'], 0)
        self.assertEqual(results['summary']['failed'], 0)

if __name__ == '__main__':
    unittest.main()
