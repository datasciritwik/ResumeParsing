import spacy
from spacy.matcher import Matcher
from typing import Dict, List, Any
import logging
from datetime import datetime
import re

from ..models.schemas import PersonalInfo, Education, Experience, ResumeData
from ..utils.patterns import RegexPatterns
from ..utils.skills_database import SkillsDatabase

logger = logging.getLogger(__name__)

class EntityExtractor:
    """Advanced NER with multiple models and rule-based extraction"""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            logger.warning(f"SpaCy model {model_name} not found. Using blank model.")
            self.nlp = spacy.blank("en")
        
        self.matcher = Matcher(self.nlp.vocab)
        self.skills_db = SkillsDatabase()
        self._setup_custom_patterns()
    
    def _setup_custom_patterns(self):
        """Setup custom spaCy patterns for better entity recognition"""
        # University patterns
        university_pattern = [
            {"LOWER": {"IN": ["university", "college", "institute", "school"]}},
            {"IS_ALPHA": True, "OP": "*"}
        ]
        self.matcher.add("UNIVERSITY", [university_pattern])
        
        # Company patterns (common suffixes)
        company_pattern = [
            {"IS_ALPHA": True, "OP": "+"},
            {"LOWER": {"IN": ["inc", "llc", "corp", "ltd", "company", "technologies", "tech", "systems"]}}
        ]
        self.matcher.add("COMPANY", [company_pattern])
        
        # Degree patterns
        degree_pattern = [
            {"LOWER": {"IN": ["bachelor", "master", "phd", "mba", "ms", "bs", "ba", "ma"]}},
            {"IS_ALPHA": True, "OP": "*"}
        ]
        self.matcher.add("DEGREE", [degree_pattern])
    
    def extract_entities(self, text: str, sections: Dict[str, str]) -> ResumeData:
        """Extract all entities from resume text"""
        doc = self.nlp(text)
        
        resume_data = ResumeData()
        
        # Extract personal information
        resume_data.personal_info = self._extract_personal_info(text, doc)
        
        # Extract section-specific information
        if 'education' in sections:
            resume_data.education = self._extract_education(sections['education'])
        
        if 'experience' in sections:
            resume_data.experience = self._extract_experience(sections['experience'])
        
        if 'skills' in sections:
            resume_data.skills = self._extract_skills(sections['skills'])
        else:
            # Fallback: extract skills from entire text
            resume_data.skills = self.skills_db.extract_skills(text)
        
        if 'summary' in sections:
            resume_data.summary = sections['summary']
        
        # Extract additional entities
        resume_data.certifications = self._extract_certifications(text)
        resume_data.languages = self._extract_languages(text)
        resume_data.projects = self._extract_projects(sections.get('projects', ''))
        
        return resume_data
    
    def _extract_personal_info(self, text: str, doc) -> PersonalInfo:
        """Extract personal contact information"""
        personal_info = PersonalInfo()
        
        # Extract email
        email_match = RegexPatterns.EMAIL.search(text)
        if email_match:
            personal_info.email = email_match.group()
        
        # Extract phone
        phone_match = RegexPatterns.PHONE.search(text)
        if phone_match:
            personal_info.phone = phone_match.group()
        
        # Extract social links
        linkedin_match = RegexPatterns.LINKEDIN.search(text)
        if linkedin_match:
            personal_info.linkedin = linkedin_match.group()
        
        github_match = RegexPatterns.GITHUB.search(text)
        if github_match:
            personal_info.github = github_match.group()
        
        # Extract name (first PERSON entity, usually at the top)
        for ent in doc.ents:
            if ent.label_ == "PERSON" and not personal_info.name:
                # Simple heuristic: name is likely in first 200 chars
                if ent.start_char < 200:
                    personal_info.name = ent.text
                    break
        
        # Extract location
        locations = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]
        if locations:
            personal_info.location = locations[0]  # Take first location
        
        return personal_info
    
    def _extract_education(self, education_text: str) -> List[Education]:
        """Extract education information"""
        education_list = []
        
        if not education_text:
            return education_list
        
        doc = self.nlp(education_text)
        
        # Split by common delimiters
        sections = re.split(r'\n(?=\w)', education_text)
        
        for section in sections:
            if len(section.strip()) < 10:  # Skip short lines
                continue
            
            education = Education()
            
            # Extract degree
            degree_match = RegexPatterns.DEGREE_PATTERNS.search(section)
            if degree_match:
                education.degree = degree_match.group().strip()
            
            # Extract GPA
            gpa_match = RegexPatterns.GPA_PATTERN.search(section)
            if gpa_match:
                education.gpa = gpa_match.group(1)
            
            # Extract institutions using NER
            section_doc = self.nlp(section)
            for ent in section_doc.ents:
                if ent.label_ == "ORG" and not education.institution:
                    education.institution = ent.text
            
            # Extract dates
            dates = self._extract_dates(section)
            if len(dates) >= 2:
                education.start_date = dates[0]
                education.end_date = dates[1]
            elif len(dates) == 1:
                education.end_date = dates[0]
            
            if education.institution or education.degree:
                education_list.append(education)
        
        return education_list
    
    def _extract_experience(self, experience_text: str) -> List[Experience]:
        """Extract work experience information"""
        experience_list = []
        
        if not experience_text:
            return experience_list
        
        # Split by job entries (usually separated by multiple newlines or job titles)
        job_sections = re.split(r'\n(?=\w.*(?:at|@|\|)|\w.*\d{4})', experience_text)
        
        for section in job_sections:
            if len(section.strip()) < 20:  # Skip short sections
                continue
            
            experience = Experience()
            
            lines = section.strip().split('\n')
            first_line = lines[0] if lines else ""
            
            # Parse first line for position and company
            # Common formats: "Position at Company", "Position | Company", "Position - Company"
            position_company_match = re.search(
                r'^(.+?)\s+(?:at|@|\||[-–—])\s+(.+?)(?:\s*\|\s*(.+?))?$',
                first_line.strip(),
                re.IGNORECASE
            )
            
            if position_company_match:
                experience.position = position_company_match.group(1).strip()
                experience.company = position_company_match.group(2).strip()
                if position_company_match.group(3):
                    experience.location = position_company_match.group(3).strip()
            else:
                # Fallback: use NER to identify organizations
                doc = self.nlp(first_line)
                orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
                if orgs:
                    experience.company = orgs[0]
                    # Assume everything before company name is position
                    company_pos = first_line.find(orgs[0])
                    if company_pos > 0:
                        experience.position = first_line[:company_pos].strip()
            
            # Extract dates
            dates = self._extract_dates(section)
            if len(dates) >= 2:
                experience.start_date = dates[0]
                experience.end_date = dates[1]
            elif len(dates) == 1:
                experience.end_date = dates[0]
            
            # Extract description (everything after first line)
            if len(lines) > 1:
                experience.description = '\n'.join(lines[1:]).strip()
            
            if experience.company or experience.position:
                experience_list.append(experience)
        
        return experience_list
    
    def _extract_skills(self, skills_text: str) -> List[str]:
        """Extract skills with enhanced detection"""
        if not skills_text:
            return []
        
        skills = self.skills_db.extract_skills(skills_text)
        
        # Additional parsing for comma/bullet-separated lists
        # Remove bullet points and split by common delimiters
        cleaned_text = re.sub(r'[•◦▪▫‣⁃*-]', '', skills_text)
        skill_candidates = re.split(r'[,;|\n]', cleaned_text)
        
        for candidate in skill_candidates:
            candidate = candidate.strip()
            if candidate and len(candidate) < 50:  # Reasonable skill name length
                # Check if it's a known skill
                found_skills = self.skills_db.extract_skills(candidate)
                skills.extend(found_skills)
        
        # Remove duplicates and return
        return list(set(skills))
    
    def _extract_dates(self, text: str) -> List[str]:
        """Extract dates from text"""
        dates = []
        
        for pattern in RegexPatterns.DATE_PATTERNS:
            matches = pattern.findall(text)
            dates.extend(matches)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_dates = []
        for date in dates:
            if date not in seen:
                seen.add(date)
                unique_dates.append(date)
        
        return unique_dates
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        cert_keywords = [
            "certified", "certification", "certificate", "license", "credential",
            "AWS", "Google Cloud", "Azure", "PMP", "CISSP", "CompTIA"
        ]
        
        certifications = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(keyword.lower() in line.lower() for keyword in cert_keywords):
                if 10 < len(line) < 100:  # Reasonable cert name length
                    certifications.append(line)
        
        return certifications
    
    def _extract_languages(self, text: str) -> List[str]:
        """Extract languages"""
        common_languages = [
            "English", "Spanish", "French", "German", "Chinese", "Japanese",
            "Korean", "Arabic", "Russian", "Portuguese", "Italian", "Dutch",
            "Hindi", "Bengali", "Mandarin", "Cantonese"
        ]
        
        languages = []
        text_lower = text.lower()
        
        for lang in common_languages:
            if lang.lower() in text_lower:
                languages.append(lang)
        
        return languages
    
    def _extract_projects(self, projects_text: str) -> List[Dict[str, Any]]:
        """Extract project information"""
        projects = []
        
        if not projects_text:
            return projects
        
        # Split by project entries
        project_sections = re.split(r'\n(?=\w.*:|\w.*[-–—])', projects_text)
        
        for section in project_sections:
            if len(section.strip()) < 20:
                continue
            
            lines = section.strip().split('\n')
            if not lines:
                continue
            
            project = {
                'name': '',
                'description': '',
                'technologies': [],
                'url': ''
            }
            
            # Extract project name (usually first line)
            first_line = lines[0].strip()
            if ':' in first_line:
                project['name'] = first_line.split(':')[0].strip()
            elif '−' in first_line or '–' in first_line or '—' in first_line:
                project['name'] = re.split(r'[-–—]', first_line)[0].strip()
            else:
                project['name'] = first_line
            
            # Extract description and technologies
            description_lines = lines[1:] if len(lines) > 1 else []
            project['description'] = '\n'.join(description_lines).strip()
            
            # Extract technologies mentioned in project description
            project['technologies'] = self.skills_db.extract_skills(section)
            
            # Extract URLs
            url_match = re.search(r'https?://[^\s]+', section)
            if url_match:
                project['url'] = url_match.group()
            
            if project['name']:
                projects.append(project)
        
        return projects