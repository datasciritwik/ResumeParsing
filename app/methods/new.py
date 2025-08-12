import fitz  # PyMuPDF
import google.generativeai as genai
import json
import os
import re
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

class LLMATSCalculator:
    def __init__(self):
        # Configure Gemini API
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("❌ GEMINI_API_KEY not found in environment variables")

        genai.configure(api_key=self.api_key)

        # Initialize Gemini 2.5 Flash-Lite model
        self.model = genai.GenerativeModel('gemini-2.0-flash-lite')

        print("✅ Gemini 2.5 Flash-Lite initialized successfully")

    def extract_text_from_pdf(self, file_path):
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

    def create_analysis_prompt(self, resume_text, jd_text):
        """Create a comprehensive prompt for LLM analysis"""
        return f"""
You are an expert ATS (Applicant Tracking System) analyzer and career consultant. Analyze the following resume against the job description and provide a comprehensive assessment.

**JOB DESCRIPTION:**
{jd_text[:4000]}  # Truncate to avoid token limits

**RESUME:**
{resume_text[:4000]}  # Truncate to avoid token limits

Please provide a detailed analysis in the following JSON format:

{{
    "ats_score": {{
        "overall_score": <number between 0-100>,
        "keyword_match_score": <number between 0-100>,
        "skills_alignment_score": <number between 0-100>,
        "experience_relevance_score": <number between 0-100>,
        "format_optimization_score": <number between 0-100>
    }},
    "skill_analysis": {{
        "matched_skills": [<list of skills found in both resume and JD>],
        "missing_critical_skills": [<list of important skills missing from resume>],
        "skill_gaps": [<list of skill areas needing improvement>],
        "transferable_skills": [<list of skills that could be highlighted better>]
    }},
    "keyword_analysis": {{
        "matched_keywords": [<list of important keywords found in both>],
        "missing_keywords": [<list of critical keywords missing from resume>],
        "keyword_density_score": <number between 0-100>
    }},
    "experience_analysis": {{
        "relevant_experience_years": <estimated years of relevant experience>,
        "experience_gaps": [<list of experience areas that could be strengthened>],
        "achievements_alignment": <how well achievements match JD requirements>
    }},
    "recommendations": {{
        "high_priority": [<list of most critical improvements needed>],
        "medium_priority": [<list of moderate improvements>],
        "low_priority": [<list of nice-to-have improvements>],
        "content_suggestions": [<specific content to add or modify>]
    }},
    "ats_optimization": {{
        "format_issues": [<list of potential ATS parsing issues>],
        "section_recommendations": [<suggestions for resume sections>],
        "keyword_placement": [<suggestions for better keyword placement>]
    }},
    "competitive_analysis": {{
        "strengths": [<candidate's competitive advantages>],
        "weaknesses": [<areas where candidate may fall short>],
        "differentiation_opportunities": [<ways to stand out>]
    }},
    "industry_insights": {{
        "industry_trends": [<relevant industry trends affecting this role>],
        "emerging_skills": [<skills becoming important in this field>],
        "market_positioning": <advice on how to position candidacy>
    }}
}}

Ensure all scores are realistic and based on actual content analysis. Be specific in recommendations and provide actionable insights.
"""

    def analyze_with_gemini(self, resume_text, jd_text):
        """Use Gemini to analyze resume against job description"""
        try:
            prompt = self.create_analysis_prompt(resume_text, jd_text)

            print("🤖 Analyzing with Gemini AI...")
            response = self.model.generate_content(prompt)

            # Extract JSON from response
            response_text = response.text

            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                analysis = json.loads(json_str)
                return analysis
            else:
                # Fallback: try to parse the entire response as JSON
                return json.loads(response_text)

        except json.JSONDecodeError as e:
            print(f"⚠️ Error parsing JSON response: {e}")
            print("Raw response:", response.text[:500] + "...")
            return self.create_fallback_analysis()
        except Exception as e:
            print(f"❌ Error with Gemini API: {e}")
            return self.create_fallback_analysis()

    def create_fallback_analysis(self):
        """Create a basic analysis structure if LLM fails"""
        return {
            "ats_score": {
                "overall_score": 50,
                "keyword_match_score": 50,
                "skills_alignment_score": 50,
                "experience_relevance_score": 50,
                "format_optimization_score": 50
            },
            "skill_analysis": {
                "matched_skills": [],
                "missing_critical_skills": [],
                "skill_gaps": [],
                "transferable_skills": []
            },
            "recommendations": {
                "high_priority": ["Unable to analyze - please check API connection"],
                "medium_priority": [],
                "low_priority": []
            },
            "error": "Analysis failed - using fallback structure"
        }

    def get_detailed_insights(self, analysis_result, resume_text, jd_text):
        """Get additional detailed insights using a second LLM call"""
        try:
            insights_prompt = f"""
Based on the previous analysis, provide additional strategic insights for this job application:

Previous Analysis Summary:
- Overall ATS Score: {analysis_result.get('ats_score', {}).get('overall_score', 'N/A')}%
- Top Missing Skills: {', '.join(analysis_result.get('skill_analysis', {}).get('missing_critical_skills', [])[:3])}

Resume Length: {len(resume_text.split())} words
JD Length: {len(jd_text.split())} words

Provide strategic insights in JSON format:
{{
    "application_strategy": {{
        "cover_letter_focus": [<key points to emphasize in cover letter>],
        "interview_preparation": [<skills/topics to prepare for interviews>],
        "portfolio_suggestions": [<projects/work to highlight>]
    }},
    "timeline_recommendations": {{
        "immediate_actions": [<things to do before applying>],
        "short_term_improvements": [<improvements for next 1-2 weeks>],
        "long_term_development": [<skills to develop over months>]
    }},
    "market_intelligence": {{
        "salary_insights": <insights about role expectations>,
        "growth_trajectory": <career path insights>,
        "alternative_roles": [<similar roles to consider>]
    }},
    "personalized_advice": {{
        "communication_style": <how to communicate value proposition>,
        "unique_selling_points": [<what makes this candidate special>],
        "risk_mitigation": [<how to address potential concerns>]
    }}
}}
"""

            print("🧠 Getting detailed insights...")
            response = self.model.generate_content(insights_prompt)

            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())

            return {"insights": "Additional insights unavailable"}

        except Exception as e:
            print(f"⚠️ Error getting detailed insights: {e}")
            return {"insights": "Additional insights unavailable"}

    def calculate_enhanced_metrics(self, analysis_result, resume_text, jd_text):
        """Calculate additional metrics"""
        metrics = {}

        # Text analysis metrics
        resume_words = len(resume_text.split())
        jd_words = len(jd_text.split())

        metrics['text_metrics'] = {
            'resume_word_count': resume_words,
            'jd_word_count': jd_words,
            'resume_to_jd_ratio': round(resume_words / max(jd_words, 1), 2)
        }

        # Skill coverage metrics
        skill_analysis = analysis_result.get('skill_analysis', {})
        matched_skills = len(skill_analysis.get('matched_skills', []))
        missing_skills = len(skill_analysis.get('missing_critical_skills', []))

        if matched_skills + missing_skills > 0:
            metrics['skill_coverage'] = round((matched_skills / (matched_skills + missing_skills)) * 100, 2)
        else:
            metrics['skill_coverage'] = 0

        # Competitiveness score
        ats_scores = analysis_result.get('ats_score', {})
        avg_score = sum(ats_scores.values()) / max(len(ats_scores), 1)

        if avg_score >= 90:
            metrics['competitiveness'] = "Extremely Competitive"
        elif avg_score >= 80:
            metrics['competitiveness'] = "Highly Competitive"
        elif avg_score >= 70:
            metrics['competitiveness'] = "Competitive"
        elif avg_score >= 60:
            metrics['competitiveness'] = "Moderately Competitive"
        else:
            metrics['competitiveness'] = "Needs Significant Improvement"

        return metrics

    def display_results(self, analysis_result, additional_insights, enhanced_metrics):
        """Display comprehensive results"""
        print("\n" + "=" * 80)
        print("🤖 LLM-POWERED ATS ANALYSIS REPORT")
        print("=" * 80)

        # Overall Score
        ats_scores = analysis_result.get('ats_score', {})
        overall = ats_scores.get('overall_score', 0)

        print(f"🎯 OVERALL ATS SCORE: {overall}%")
        print(f"📊 COMPETITIVENESS: {enhanced_metrics.get('competitiveness', 'N/A')}")

        # Detailed Scores
        print(f"\n📈 DETAILED BREAKDOWN:")
        print(f"   ├─ Keyword Matching: {ats_scores.get('keyword_match_score', 0)}%")
        print(f"   ├─ Skills Alignment: {ats_scores.get('skills_alignment_score', 0)}%")
        print(f"   ├─ Experience Relevance: {ats_scores.get('experience_relevance_score', 0)}%")
        print(f"   └─ Format Optimization: {ats_scores.get('format_optimization_score', 0)}%")

        # Skills Analysis
        skill_analysis = analysis_result.get('skill_analysis', {})
        print(f"\n🛠️ SKILLS ANALYSIS:")
        print(f"   ├─ Skill Coverage: {enhanced_metrics.get('skill_coverage', 0)}%")
        print(f"   ├─ Matched Skills: {len(skill_analysis.get('matched_skills', []))}")
        print(f"   └─ Missing Critical Skills: {len(skill_analysis.get('missing_critical_skills', []))}")

        if skill_analysis.get('matched_skills'):
            print(f"\n✅ TOP MATCHED SKILLS:")
            for i, skill in enumerate(skill_analysis['matched_skills'][:8], 1):
                print(f"   {i}. {skill}")

        if skill_analysis.get('missing_critical_skills'):
            print(f"\n❌ MISSING CRITICAL SKILLS:")
            for i, skill in enumerate(skill_analysis['missing_critical_skills'][:8], 1):
                print(f"   {i}. {skill}")

        # High Priority Recommendations
        recommendations = analysis_result.get('recommendations', {})
        if recommendations.get('high_priority'):
            print(f"\n🚨 HIGH PRIORITY IMPROVEMENTS:")
            for i, rec in enumerate(recommendations['high_priority'][:5], 1):
                print(f"   {i}. {rec}")

        # Application Strategy from Additional Insights
        app_strategy = additional_insights.get('application_strategy', {})
        if app_strategy.get('cover_letter_focus'):
            print(f"\n📝 COVER LETTER FOCUS POINTS:")
            for i, point in enumerate(app_strategy['cover_letter_focus'][:3], 1):
                print(f"   {i}. {point}")

        # Timeline Recommendations
        timeline = additional_insights.get('timeline_recommendations', {})
        if timeline.get('immediate_actions'):
            print(f"\n⏰ IMMEDIATE ACTIONS:")
            for i, action in enumerate(timeline['immediate_actions'][:3], 1):
                print(f"   {i}. {action}")

    def comprehensive_report(self, analysis_result, additional_insights, enhanced_metrics):
        """Save detailed report to file"""
        timestamp = datetime.now().isoformat()

        report = {
            'metadata': {
                'timestamp': timestamp,
                'analysis_engine': 'Gemini 2.5 Flash-Lite'
            },
            'analysis_results': analysis_result,
            'additional_insights': additional_insights,
            'enhanced_metrics': enhanced_metrics,
            'text_metrics': enhanced_metrics.get('text_metrics', {})
        }

        return report

    def run_analysis(self, jd_text, resume_text):
        """Main method to run the complete analysis"""

        # Run main analysis
        analysis_result = self.analyze_with_gemini(resume_text, jd_text)

        # Get additional insights
        additional_insights = self.get_detailed_insights(analysis_result, resume_text, jd_text)

        # Calculate enhanced metrics
        enhanced_metrics = self.calculate_enhanced_metrics(analysis_result, resume_text, jd_text)

        output = self.comprehensive_report(analysis_result, additional_insights, enhanced_metrics)

        return output