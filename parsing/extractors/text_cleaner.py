import re
from typing import List, Dict, Tuple, Optional

class TextCleaner:
    """Advanced text preprocessing and cleaning for resume parsing"""
    
    def __init__(self):
        self.noise_patterns = self._compile_noise_patterns()
        self.section_patterns = self._compile_resume_section_patterns()
        self.contact_patterns = self._compile_contact_patterns()
    
    def _compile_noise_patterns(self) -> List[re.Pattern]:
        """Compile patterns for removing noise"""
        return [
            re.compile(r'\s+'),  # Multiple whitespace
            re.compile(r'\n\s*\n'),  # Multiple newlines
            re.compile(r'[^\w\s@.-]', re.UNICODE),  # Special chars (keep email/phone chars)
            re.compile(r'(?i)page\s*\d+\s*of\s*\d+'),  # Page numbers
            re.compile(r'(?i)confidential|proprietary'),  # Headers/footers
        ]
    
    def _compile_resume_section_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Compile patterns for detecting resume section headers"""
        return {
            'contact_info': [
                re.compile(r'^\s*contact\s*(?:info|information)?\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*personal\s*(?:info|information|details)?\s*:?\s*$', re.IGNORECASE),
            ],
            'summary': [
                re.compile(r'^\s*(?:professional\s+)?summary\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*(?:career\s+)?(?:summary|overview)\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*(?:executive\s+)?summary\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*profile\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*about\s*(?:me)?\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*objective\s*:?\s*$', re.IGNORECASE),
            ],
            'experience': [
                re.compile(r'^\s*(?:work\s+)?experience\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*(?:professional\s+)?experience\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*employment\s*(?:history)?\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*work\s*(?:history)?\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*career\s*(?:history)?\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*positions?\s*(?:held)?\s*:?\s*$', re.IGNORECASE),
            ],
            'education': [
                re.compile(r'^\s*education\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*educational\s*(?:background|qualifications?)?\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*academic\s*(?:background)?\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*qualifications?\s*:?\s*$', re.IGNORECASE),
            ],
            'skills': [
                re.compile(r'^\s*skills?\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*(?:technical\s+)?skills?\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*(?:core\s+)?competencies\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*(?:key\s+)?skills?\s*(?:and\s+competencies)?\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*expertise\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*technologies?\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*technical\s*(?:knowledge|expertise)?\s*:?\s*$', re.IGNORECASE),
            ],
            'projects': [
                re.compile(r'^\s*projects?\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*(?:key\s+)?projects?\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*(?:notable\s+)?projects?\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*project\s*(?:experience|work)?\s*:?\s*$', re.IGNORECASE),
            ],
            'certifications': [
                re.compile(r'^\s*certifications?\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*certificates?\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*(?:professional\s+)?certifications?\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*licenses?\s*(?:and\s+certifications?)?\s*:?\s*$', re.IGNORECASE),
            ],
            'achievements': [
                re.compile(r'^\s*achievements?\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*accomplishments?\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*awards?\s*(?:and\s+achievements?)?\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*honors?\s*(?:and\s+awards?)?\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*recognition\s*:?\s*$', re.IGNORECASE),
            ],
            'languages': [
                re.compile(r'^\s*languages?\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*language\s*(?:skills|proficiency)?\s*:?\s*$', re.IGNORECASE),
            ],
            'interests': [
                re.compile(r'^\s*interests?\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*hobbies?\s*(?:and\s+interests?)?\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*personal\s*interests?\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*activities?\s*:?\s*$', re.IGNORECASE),
            ],
            'references': [
                re.compile(r'^\s*references?\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*professional\s*references?\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*references?\s*available\s*(?:upon\s+request)?\s*:?\s*$', re.IGNORECASE),
            ],
            'volunteer': [
                re.compile(r'^\s*volunteer\s*(?:experience|work)?\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*volunteering\s*:?\s*$', re.IGNORECASE),
                re.compile(r'^\s*community\s*(?:service|involvement)?\s*:?\s*$', re.IGNORECASE),
            ]
        }
    
    def _compile_contact_patterns(self) -> Dict[str, re.Pattern]:
        """Patterns for identifying contact information"""
        return {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone': re.compile(r'(\+?1?[-.\s]?)?(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})'),
            'linkedin': re.compile(r'(?:linkedin\.com/in/|linkedin\.com/pub/)([A-Za-z0-9-]+)', re.IGNORECASE),
            'github': re.compile(r'(?:github\.com/)([A-Za-z0-9-]+)', re.IGNORECASE),
        }
    
    def clean(self, text: str) -> str:
        """Comprehensive text cleaning for resumes"""
        if not text:
            return ""
        
        # Remove page markers and common resume noise
        text = re.sub(r'--- PAGE \d+ ---', '', text)
        text = re.sub(r'Resume of\s+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Curriculum Vitae', '', text, flags=re.IGNORECASE)
        
        # Normalize Unicode characters
        text = self._normalize_unicode(text)
        
        # Fix common OCR errors
        text = self._fix_ocr_errors(text)
        
        # Remove noise patterns
        text = self._remove_noise(text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n', text)
        
        return text.strip()
    
    def _normalize_unicode(self, text: str) -> str:
        """Normalize Unicode characters"""
        replacements = {
            '\u2022': '•',  # Bullet point
            '\u2013': '-',  # En dash
            '\u2014': '-',  # Em dash
            '\u2018': "'",  # Left single quote
            '\u2019': "'",  # Right single quote
            '\u201c': '"',  # Left double quote
            '\u201d': '"',  # Right double quote
            '\u00a0': ' ',  # Non-breaking space
        }
        
        for unicode_char, replacement in replacements.items():
            text = text.replace(unicode_char, replacement)
        
        return text
    
    def _fix_ocr_errors(self, text: str) -> str:
        """Fix common OCR errors"""
        ocr_fixes = {
            r'\bl\b': 'I',  # lowercase l to uppercase I
            r'\b0\b': 'O',  # zero to letter O in names
            r'(\w)l(\w)': r'\1I\2',  # l to I in middle of words
        }
        
        for pattern, replacement in ocr_fixes.items():
            text = re.sub(pattern, replacement, text)
        
        return text
    
    def _remove_noise(self, text: str) -> str:
        """Remove noise patterns"""
        # Remove excessive punctuation
        text = re.sub(r'[.]{3,}', '...', text)
        text = re.sub(r'[-]{3,}', '---', text)
        
        # Remove standalone numbers (likely page numbers)
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        
        return text
    
    def _is_section_header(self, line: str) -> Optional[str]:
        """Check if a line is a resume section header"""
        line = line.strip()
        
        # Skip very short or very long lines
        if len(line) < 2 or len(line) > 50:
            return None
        
        # Check against resume section patterns
        for section_name, patterns in self.section_patterns.items():
            for pattern in patterns:
                if pattern.match(line):
                    return section_name
        
        # Check for common resume header styles
        # ALL CAPS headers
        if line.isupper() and len(line.split()) <= 4:
            line_lower = line.lower().replace(':', '').strip()
            for section_name, patterns in self.section_patterns.items():
                for pattern in patterns:
                    # Extract the core pattern without regex anchors
                    core_pattern = pattern.pattern.replace(r'^\s*', '').replace(r'\s*:?\s*$', '')
                    core_pattern = core_pattern.replace(r'(?:', '').replace(r')?', '').replace(r'\s+', r'\s*')
                    if re.match(core_pattern, line_lower, re.IGNORECASE):
                        return section_name
        
        # Bold or emphasized headers (look for patterns like "**EXPERIENCE**")
        bold_match = re.match(r'^\*\*(.+)\*\*$', line)
        if bold_match:
            return self._is_section_header(bold_match.group(1))
        
        return None
    
    def _is_likely_resume_header(self, line: str, context_lines: List[str] = None) -> bool:
        """Determine if a line is likely a resume section header using heuristics"""
        line = line.strip()
        
        if not line or len(line) < 3:
            return False
        
        # Too long to be a header
        if len(line) > 40:
            return False
        
        # Contains contact info patterns (likely not a header)
        for pattern in self.contact_patterns.values():
            if pattern.search(line):
                return False
        
        # Check for title case or all caps
        words = line.split()
        if len(words) <= 4:
            # Title case check
            title_case_count = sum(1 for word in words if word[0].isupper())
            if title_case_count >= len(words) * 0.7:
                return True
            
            # All caps check
            if line.isupper():
                return True
        
        # Ends with colon
        if line.endswith(':'):
            return True
        
        # Check if it's underlined (next line is dashes/equals)
        if context_lines and len(context_lines) > 0:
            next_line = context_lines[0].strip()
            if next_line and len(next_line) >= len(line) * 0.5:
                if all(c in '=-_*' for c in next_line):
                    return True
        
        return False
    
    def _extract_name_from_header(self, text: str) -> Optional[str]:
        """Try to extract candidate name from the beginning of resume"""
        lines = text.split('\n')[:5]  # Check first 5 lines
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip lines with contact info
            has_contact = any(pattern.search(line) for pattern in self.contact_patterns.values())
            if has_contact:
                continue
            
            # Skip lines that look like section headers
            if self._is_section_header(line):
                continue
            
            # Look for name patterns (2-4 words, title case, no numbers)
            words = line.split()
            if 2 <= len(words) <= 4:
                if all(word[0].isupper() and word.isalpha() for word in words):
                    return line
        
        return None
    
    def extract_sections(self, text: str, min_section_length: int = 5) -> Dict[str, str]:
        """
        Extract resume sections with improved detection for resume formats
        
        Args:
            text: Input resume text
            min_section_length: Minimum characters for a valid section
            
        Returns:
            Dictionary mapping section names to their content
        """
        if not text:
            return {'other': ''}
        
        lines = text.split('\n')
        sections = {}
        current_section = 'header'  # Start with header section for name/contact
        section_content = []
        
        # Try to extract name first
        candidate_name = self._extract_name_from_header(text)
        if candidate_name:
            sections['name'] = candidate_name
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines but preserve structure
            if not line:
                if section_content:
                    section_content.append('')
                i += 1
                continue
            
            # Get context for header detection
            context_lines = [lines[j].strip() for j in range(i+1, min(i+3, len(lines)))]
            
            # Check for section headers
            section_name = self._is_section_header(line)
            
            # If not a defined section, check if it looks like a header
            if not section_name and self._is_likely_resume_header(line, context_lines):
                # Create section name from header text
                clean_name = re.sub(r'[^\w\s]', '', line).strip().lower()
                clean_name = re.sub(r'\s+', '_', clean_name)
                if clean_name and len(clean_name) <= 30:
                    section_name = clean_name
            
            if section_name:
                # Handle underlined headers
                if context_lines and context_lines[0] and all(c in '=-_*' for c in context_lines[0]):
                    i += 1  # Skip the underline
                
                # Save previous section
                if section_content and current_section:
                    content = '\n'.join(section_content).strip()
                    if len(content) >= min_section_length:
                        # Merge with existing section if it already exists
                        if current_section in sections:
                            sections[current_section] += '\n\n' + content
                        else:
                            sections[current_section] = content
                
                # Start new section
                current_section = section_name
                section_content = []
                
                # Check if header line contains content
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) > 1 and parts[1].strip():
                        section_content.append(parts[1].strip())
            
            else:
                # Regular content line
                section_content.append(line)
            
            i += 1
        
        # Save final section
        if section_content and current_section:
            content = '\n'.join(section_content).strip()
            if len(content) >= min_section_length:
                if current_section in sections:
                    sections[current_section] += '\n\n' + content
                else:
                    sections[current_section] = content
        
        # If no sections found, treat as unstructured resume
        if len(sections) <= 1:  # Only name or empty
            sections['content'] = text.strip()
        
        # Extract contact info from any section
        self._extract_contact_info(sections)
        
        return sections
    
    def _extract_contact_info(self, sections: Dict[str, str]) -> None:
        """Extract contact information and add to sections"""
        contact_info = {}
        
        # Search all sections for contact info
        all_text = ' '.join(sections.values())
        
        for contact_type, pattern in self.contact_patterns.items():
            matches = pattern.findall(all_text)
            if matches:
                if contact_type == 'phone':
                    # Clean phone number
                    contact_info[contact_type] = re.sub(r'[^\d+]', '', matches[0][1] if isinstance(matches[0], tuple) else matches[0])
                else:
                    contact_info[contact_type] = matches[0]
        
        if contact_info:
            sections['contact_info'] = '\n'.join(f"{k}: {v}" for k, v in contact_info.items())
    
    def get_section_summary(self, sections: Dict[str, str]) -> Dict[str, Dict]:
        """Get summary statistics for extracted resume sections"""
        summary = {}
        for section_name, content in sections.items():
            summary[section_name] = {
                'char_count': len(content),
                'word_count': len(content.split()),
                'line_count': len(content.split('\n')),
                'has_bullets': '•' in content or '*' in content,
                'has_dates': bool(re.search(r'\b\d{4}\b', content)),
            }
        return summary

# Example usage for resume parsing
if __name__ == "__main__":
    cleaner = TextCleaner()
    
    # Test with sample resume text
    sample_resume = """
    John Doe
    Software Engineer
    john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe
    
    PROFESSIONAL SUMMARY
    Experienced software engineer with 5+ years developing web applications.
    
    EXPERIENCE
    Senior Software Engineer | ABC Company | 2020-2023
    • Developed full-stack web applications using React and Node.js
    • Led team of 3 developers on multiple projects
    
    Software Engineer | XYZ Corp | 2018-2020
    • Built REST APIs and microservices
    • Improved application performance by 40%
    
    EDUCATION
    Bachelor of Science in Computer Science
    University of Technology | 2018
    
    SKILLS
    • Programming: Python, JavaScript, Java
    • Frameworks: React, Node.js, Django
    • Databases: PostgreSQL, MongoDB
    
    PROJECTS
    E-commerce Platform
    Built a full-stack e-commerce application with payment integration
    """
    
    sections = cleaner.extract_sections(sample_resume)
    print("Extracted Resume Sections:")
    print("=" * 50)
    
    for name, content in sections.items():
        print(f"\n[{name.upper().replace('_', ' ')}]")
        print("-" * 30)
        print(content[:200] + "..." if len(content) > 200 else content)
        
    print("\n\nSection Summary:")
    summary = cleaner.get_section_summary(sections)
    for name, stats in summary.items():
        print(f"{name}: {stats['word_count']} words, {stats['line_count']} lines")