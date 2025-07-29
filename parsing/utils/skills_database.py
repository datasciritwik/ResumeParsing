from typing import Dict, List

class SkillsDatabase:
    """Enhanced skills detection with categorization and fuzzy matching"""
    
    def __init__(self):
        self.skills_db = self._load_skills_database()
        self.skill_variations = self._create_skill_variations()
    
    def _load_skills_database(self) -> Dict[str, List[str]]:
        """Load comprehensive skills database"""
        return {
            "programming_languages": [
                "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust",
                "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB", "Perl",
                "Objective-C", "Dart", "Elixir", "Haskell", "Julia", "Clojure"
            ],
            "web_technologies": [
                "React", "Angular", "Vue.js", "Node.js", "Express.js", "Django",
                "Flask", "Spring Boot", "ASP.NET", "Laravel", "Rails", "FastAPI",
                "Next.js", "Nuxt.js", "Svelte", "GraphQL", "REST API", "WebSocket"
            ],
            "databases": [
                "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch",
                "Cassandra", "Neo4j", "DynamoDB", "SQLite", "Oracle", "SQL Server",
                "MariaDB", "CouchDB", "InfluxDB", "Amazon RDS"
            ],
            "cloud_platforms": [
                "AWS", "Azure", "Google Cloud", "GCP", "Heroku", "DigitalOcean",
                "Kubernetes", "Docker", "Terraform", "CloudFormation", "Ansible",
                "Jenkins", "GitLab CI", "GitHub Actions", "CircleCI"
            ],
            "data_science": [
                "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
                "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy",
                "Matplotlib", "Seaborn", "Jupyter", "Apache Spark", "Hadoop",
                "Tableau", "Power BI", "Apache Kafka", "Apache Airflow"
            ],
            "mobile_development": [
                "React Native", "Flutter", "Android", "iOS", "Xamarin",
                "Ionic", "Cordova", "Unity", "Unreal Engine"
            ],
            "soft_skills": [
                "Leadership", "Communication", "Problem Solving", "Team Work",
                "Project Management", "Agile", "Scrum", "Critical Thinking",
                "Analytical Thinking", "Creativity", "Adaptability"
            ]
        }
    
    def _create_skill_variations(self) -> Dict[str, str]:
        """Create variations and aliases for skills"""
        variations = {}
        for category, skills in self.skills_db.items():
            for skill in skills:
                # Add lowercase version
                variations[skill.lower()] = skill
                # Add common variations
                if skill == "JavaScript":
                    variations["js"] = skill
                elif skill == "TypeScript":
                    variations["ts"] = skill
                elif skill == "Python":
                    variations["python3"] = skill
                # Add more variations as needed
        return variations
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text with fuzzy matching"""
        text_lower = text.lower()
        found_skills = set()
        
        # Direct matching
        for skill_lower, skill_original in self.skill_variations.items():
            if skill_lower in text_lower:
                found_skills.add(skill_original)
        
        # Additional pattern-based extraction for frameworks/libraries
        framework_patterns = [
            r'\b(\w+)\.js\b',  # JavaScript frameworks
            r'\b(\w+)SQL\b',   # SQL variants
            r'\bApache\s+(\w+)\b',  # Apache projects
        ]
        
        import re
        for pattern in framework_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Check if it's a known technology
                full_name = f"{match}.js" if pattern.endswith(r'\.js\b') else match
                if full_name in self.skill_variations.values():
                    found_skills.add(full_name)
        
        return list(found_skills)