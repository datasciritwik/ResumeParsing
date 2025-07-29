import re
from typing import Dict, Pattern, List

class RegexPatterns:
    """Compiled regex patterns for better performance"""
    
    # Contact Information
    EMAIL: Pattern = re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        re.IGNORECASE
    )
    
    PHONE: Pattern = re.compile(
        r'(?:\+?1[-.\s]?)?(?:\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})|'
        r'(?:\+?[1-9]\d{1,14})',
        re.MULTILINE
    )
    
    # Social Links
    LINKEDIN: Pattern = re.compile(
        r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-_]+/?',
        re.IGNORECASE
    )
    
    GITHUB: Pattern = re.compile(
        r'(?:https?://)?(?:www\.)?github\.com/[\w\-_]+/?',
        re.IGNORECASE
    )
    
    # Dates
    DATE_PATTERNS: List[Pattern] = [
        re.compile(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b', re.IGNORECASE),
        re.compile(r'\b\d{1,2}/\d{1,2}/\d{4}\b'),
        re.compile(r'\b\d{4}\s*[-–—]\s*\d{4}\b'),
        re.compile(r'\b\d{4}\s*[-–—]\s*(?:Present|Current|Now)\b', re.IGNORECASE),
    ]
    
    # Education patterns
    DEGREE_PATTERNS: Pattern = re.compile(
        r'\b(?:Bachelor|Master|PhD|Ph\.D|MBA|MS|BS|BA|MA|M\.S\.|B\.S\.|B\.A\.|M\.A\.)'
        r'(?:\s+(?:of|in|degree))?\s+[\w\s&,-]+',
        re.IGNORECASE
    )
    
    # GPA pattern
    GPA_PATTERN: Pattern = re.compile(
        r'(?:GPA|Grade Point Average)[\s:]*(\d+\.?\d*)\s*(?:/\s*\d+\.?\d*)?',
        re.IGNORECASE
    )
    
    # Section headers
    SECTION_HEADERS: Dict[str, Pattern] = {
        'education': re.compile(r'\b(?:EDUCATION|ACADEMIC|QUALIFICATION)S?\b', re.IGNORECASE),
        'experience': re.compile(r'\b(?:EXPERIENCE|EMPLOYMENT|WORK|CAREER|PROFESSIONAL)\b', re.IGNORECASE),
        'skills': re.compile(r'\b(?:SKILLS|COMPETENCIES|TECHNICAL|TECHNOLOGIES)\b', re.IGNORECASE),
        'projects': re.compile(r'\b(?:PROJECTS|PORTFOLIO)\b', re.IGNORECASE),
        'certifications': re.compile(r'\b(?:CERTIFICATIONS?|CERTIFICATES?|LICENSES?)\b', re.IGNORECASE),
        'summary': re.compile(r'\b(?:SUMMARY|PROFILE|OBJECTIVE|ABOUT)\b', re.IGNORECASE),
    }