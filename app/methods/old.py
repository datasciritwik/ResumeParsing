from nltk.corpus import wordnet
from app.utils.synonym import SKILL_SYNONYMS
import re, fitz
from rapidfuzz import fuzz, process
import spacy
from sentence_transformers import SentenceTransformer, util

nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_wordnet_synonyms(word):
    """Get synonyms from WordNet"""
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().replace('_', ' ').lower())
    return synonyms

def expand_synonyms():
    """Expand the synonym map with WordNet synonyms"""
    expanded_map = {}

    # Add original mappings
    for key, values in SKILL_SYNONYMS.items():
        all_synonyms = set([key] + values)

        # Add WordNet synonyms for technical terms (limited to avoid noise)
        if len(key.split()) <= 2:  # Only for short terms to avoid noise
            wordnet_syns = get_wordnet_synonyms(key)
            # Filter out overly generic synonyms
            filtered_syns = {syn for syn in wordnet_syns if len(syn) > 2 and syn not in ['use', 'work', 'go', 'run']}
            all_synonyms.update(list(filtered_syns)[:3])  # Limit to 3 WordNet synonyms

        expanded_map[key] = list(all_synonyms)

    return expanded_map

def normalize_skill_terms(text):
    """Normalize skill terms using comprehensive synonym mapping"""
    expanded_synonyms = expand_synonyms()
    normalized_text = text.lower()

    # Create reverse mapping for efficient lookup
    term_to_canonical = {}
    for canonical, synonyms in expanded_synonyms.items():
        for synonym in synonyms:
            term_to_canonical[synonym.lower()] = canonical

    # Replace terms with canonical forms
    words = normalized_text.split()
    normalized_words = []

    for word in words:
        # Clean word
        clean_word = re.sub(r'[^\w\s]', '', word)
        if clean_word in term_to_canonical:
            normalized_words.append(term_to_canonical[clean_word])
        else:
            normalized_words.append(clean_word)

    return ' '.join(normalized_words)

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file with better error handling."""
    try:
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def extract_skills_and_keywords(text):
    """Extract skills and keywords with better processing"""
    # Normalize text first
    normalized_text = normalize_skill_terms(text)

    doc = nlp(normalized_text)

    # Extract various types of important terms
    keywords = set()

    # Named entities (especially ORG, PRODUCT, PERSON for technologies)
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT", "PERSON", "GPE"]:
            keywords.add(ent.text.lower().strip())

    # Noun phrases that might be skills
    for chunk in doc.noun_chunks:
        if len(chunk.text.split()) <= 3 and len(chunk.text) > 2:
            keywords.add(chunk.text.lower().strip())

    # Individual tokens (filtered)
    for token in doc:
        if (token.is_alpha and not token.is_stop and
            len(token.text) > 2 and token.pos_ in ["NOUN", "PROPN", "ADJ"]):
            keywords.add(token.lemma_.lower())

    # Extract technical patterns (version numbers, frameworks, etc.)
    tech_patterns = re.findall(r'\b[a-zA-Z]+[0-9]+(?:\.[0-9]+)*\b', text.lower())
    keywords.update(tech_patterns)

    # Extract acronyms
    acronyms = re.findall(r'\b[A-Z]{2,}\b', text)
    keywords.update([acr.lower() for acr in acronyms])

    return keywords

def fuzzy_match_skills(resume_skills, jd_skills, threshold=85):
    """Enhanced fuzzy matching with better scoring"""
    matched_skills = set()
    skill_scores = {}

    for jd_skill in jd_skills:
        best_match = process.extractOne(
            jd_skill,
            resume_skills,
            scorer=fuzz.token_sort_ratio,
            score_cutoff=threshold
        )

        if best_match:
            matched_skills.add(jd_skill)
            skill_scores[jd_skill] = best_match[1]

    return matched_skills, skill_scores

def calculate_enhanced_ats_score(resume_text, jd_text):
    """Enhanced ATS score calculation with multiple factors"""

    # 1. Semantic Similarity
    resume_emb = model.encode([resume_text], convert_to_tensor=True)
    jd_emb = model.encode([jd_text], convert_to_tensor=True)
    semantic_score = float(util.cos_sim(resume_emb, jd_emb)) * 100

    # 2. Skill/Keyword Matching
    resume_skills = extract_skills_and_keywords(resume_text)
    jd_skills = extract_skills_and_keywords(jd_text)

    matched_skills, skill_scores = fuzzy_match_skills(resume_skills, jd_skills, threshold=85)

    if jd_skills:
        skill_match_score = len(matched_skills) / len(jd_skills) * 100
    else:
        skill_match_score = 0

    # 3. Critical Skills Analysis (high-weight skills)
    critical_skills = {"python", "java", "javascript", "react", "sql", "aws", "docker", "kubernetes"}
    jd_critical = jd_skills.intersection(critical_skills)
    resume_critical = resume_skills.intersection(critical_skills)

    if jd_critical:
        critical_match_score = len(jd_critical.intersection(resume_critical)) / len(jd_critical) * 100
    else:
        critical_match_score = 100  # No critical skills required

    # 4. Text Length and Structure Analysis
    resume_words = len(resume_text.split())
    jd_words = len(jd_text.split())

    # Penalize very short resumes or very long ones compared to JD
    length_ratio = min(resume_words / max(jd_words, 100), 2.0)  # Cap at 2x
    length_score = max(0, 100 - abs(1 - length_ratio) * 50)

    # 5. Final Weighted Score
    final_score = (
        semantic_score * 0.40 +      # 40% semantic similarity
        skill_match_score * 0.35 +   # 35% skill matching
        critical_match_score * 0.20 + # 20% critical skills
        length_score * 0.05          # 5% document structure
    )

    missing_skills = jd_skills - matched_skills

    return {
        'semantic_score': round(semantic_score, 2),
        'skill_match_score': round(skill_match_score, 2),
        'critical_match_score': round(critical_match_score, 2),
        'length_score': round(length_score, 2),
        'final_score': round(final_score, 2),
        'matched_skills': list(matched_skills),
        'missing_skills': list(missing_skills),
        'skill_scores': skill_scores,
        'total_jd_skills': len(jd_skills),
        'total_resume_skills': len(resume_skills)
    }

def generate_improvement_suggestions(results):
    """Generate actionable improvement suggestions"""
    suggestions = []

    if results['final_score'] < 70:
        suggestions.append("🔴 CRITICAL: ATS score is below recommended threshold (70%)")
    elif results['final_score'] < 85:
        suggestions.append("🟡 MODERATE: ATS score has room for improvement")
    else:
        suggestions.append("🟢 GOOD: ATS score is competitive")

    # Missing skills suggestions
    if results['missing_skills']:
        top_missing = sorted(list(results['missing_skills']))[:5]
        suggestions.append(f"📝 ADD MISSING SKILLS: {', '.join(top_missing)}")

    # Semantic similarity suggestions
    if results['semantic_score'] < 70:
        suggestions.append("📄 IMPROVE CONTENT ALIGNMENT: Use more keywords from the job description")

    # Critical skills suggestions
    if results['critical_match_score'] < 80:
        suggestions.append("⚡ HIGHLIGHT CRITICAL SKILLS: Emphasize key technical skills more prominently")

    return suggestions