"""
Enhanced Interview Copilot with configuration support and improved features
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import random
from config import InterviewCopilotConfig, DEFAULT_CONFIG

class QuestionType(Enum):
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    SITUATIONAL = "situational"
    GENERAL = "general"
    NOT_QUESTION = "not_question"

@dataclass
class PersonalData:
    """Container for personal interview data"""
    resume_highlights: List[str]
    star_stories: List[Dict[str, str]]
    technical_projects: List[Dict[str, str]]
    skills: List[str]
    experience: List[Dict[str, str]]

class EnhancedInterviewCopilot:
    """Enhanced copilot with configuration support and improved answer generation"""
    
    def __init__(self, personal_data: Optional[PersonalData] = None, 
                 config: Optional[InterviewCopilotConfig] = None):
        self.personal_data = personal_data or self._load_default_data()
        self.config = config or DEFAULT_CONFIG
        self.question_patterns = self._initialize_question_patterns()
    
    def _initialize_question_patterns(self) -> Dict[QuestionType, List[str]]:
        """Initialize regex patterns for question type detection"""
        base_patterns = {
            QuestionType.BEHAVIORAL: [
                r"tell me about a time",
                r"describe a situation",
                r"give me an example",
                r"when have you",
                r"how did you handle",
                r"how do you handle",
                r"what would you do if",
                r"describe your experience with",
                r"walk me through",
                r"share an example"
            ],
            QuestionType.TECHNICAL: [
                r"what is",
                r"how does.*work",
                r"explain.*algorithm",
                r"what's the difference between",
                r"how would you implement",
                r"what are the pros and cons",
                r"which approach would you",
                r"how do you optimize"
            ]
        }
        
        # Add custom patterns from config
        base_patterns[QuestionType.BEHAVIORAL].extend(self.config.custom_behavioral_patterns)
        base_patterns[QuestionType.TECHNICAL].extend(self.config.custom_technical_patterns)
        
        return base_patterns
    
    def process_input(self, transcribed_text: str) -> str:
        """Main processing function with enhanced features"""
        text = self._clean_text(transcribed_text)
        
        if not self._is_question(text):
            return "No suggestion – not a question."
        
        question_type = self._classify_question(text)
        answer = self._generate_answer(text, question_type)
        
        return self._format_final_answer(answer, question_type)
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize the transcribed text"""
        return text.strip().lower()
    
    def _is_question(self, text: str) -> bool:
        """Enhanced question detection with confidence scoring"""
        question_indicators = [
            (text.endswith('?'), 1.0),
            (text.startswith(('what', 'how', 'why', 'when', 'where', 'who')), 0.9),
            (text.startswith(('can you', 'could you', 'would you', 'do you')), 0.8),
            (text.startswith(('tell me', 'describe', 'explain')), 0.8),
            ('tell me about' in text, 0.9),
            ('give me an example' in text, 0.9),
            ('walk me through' in text, 0.8)
        ]
        
        max_confidence = max([score for condition, score in question_indicators if condition], default=0)
        return max_confidence >= self.config.question_confidence_threshold
    
    def _classify_question(self, text: str) -> QuestionType:
        """Enhanced question classification"""
        scores = {question_type: 0 for question_type in QuestionType}
        
        for question_type, patterns in self.question_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    scores[question_type] += 1
        
        # Return type with highest score
        best_type = max(scores, key=scores.get)
        return best_type if scores[best_type] > 0 else QuestionType.GENERAL
    
    def _generate_answer(self, text: str, question_type: QuestionType) -> str:
        """Generate answer with improved logic"""
        if question_type == QuestionType.BEHAVIORAL:
            return self._generate_behavioral_answer(text)
        elif question_type == QuestionType.TECHNICAL:
            return self._generate_technical_answer(text)
        else:
            return self._generate_general_answer(text)
    
    def _generate_behavioral_answer(self, text: str) -> str:
        """Enhanced behavioral answer generation"""
        relevant_story = self._find_relevant_story(text)
        
        if relevant_story:
            return self._format_star_answer(relevant_story)
        else:
            return self._generate_contextual_behavioral_answer(text)
    
    def _generate_technical_answer(self, text: str) -> str:
        """Enhanced technical answer generation"""
        # Check for relevant technical projects or skills
        relevant_context = self._find_relevant_technical_context(text)
        
        if relevant_context:
            return self._format_technical_answer_with_context(text, relevant_context)
        else:
            return self._generate_generic_technical_answer(text)
    
    def _find_relevant_story(self, text: str) -> Optional[Dict[str, str]]:
        """Enhanced story matching with keyword scoring"""
        if not self.personal_data or not self.personal_data.star_stories:
            return None
        
        question_keywords = [word for word in text.split() if len(word) > 3]
        best_story = None
        best_score = 0
        
        for story in self.personal_data.star_stories:
            score = 0
            story_parts = []
            
            for value in story.values():
                if isinstance(value, list):
                    story_parts.extend([str(item) for item in value])
                else:
                    story_parts.append(str(value))
            
            story_text = ' '.join(story_parts).lower()
            
            # Enhanced keyword matching
            for keyword in question_keywords:
                if keyword in story_text:
                    score += 2  # Base score
                    # Bonus for exact phrase matches
                    if f" {keyword} " in f" {story_text} ":
                        score += 1
            
            # Bonus for stories with explicit keywords field
            if 'keywords' in story and isinstance(story['keywords'], list):
                for story_keyword in story['keywords']:
                    if any(keyword in story_keyword.lower() for keyword in question_keywords):
                        score += 3
            
            if score > best_score and score >= self.config.keyword_matching_threshold:
                best_score = score
                best_story = story
        
        return best_story
    
    def _find_relevant_technical_context(self, text: str) -> Optional[Dict[str, str]]:
        """Find relevant technical projects or skills"""
        if not self.personal_data:
            return None
        
        question_keywords = text.split()
        
        # Check technical projects
        for project in self.personal_data.technical_projects:
            project_text = ' '.join([str(v) for v in project.values()]).lower()
            for keyword in question_keywords:
                if keyword in project_text:
                    return {"type": "project", "data": project}
        
        # Check skills
        for skill in self.personal_data.skills:
            if any(keyword in skill.lower() for keyword in question_keywords):
                return {"type": "skill", "data": {"skill": skill}}
        
        return None
    
    def _format_star_answer(self, story: Dict[str, str]) -> str:
        """Enhanced STAR answer formatting"""
        situation = story.get('situation', '')
        task = story.get('task', '')
        action = story.get('action', '')
        result = story.get('result', '')
        
        # Create natural flow with appropriate connectors
        parts = []
        if situation:
            parts.append(situation)
        if task:
            connector = " " if not situation else " "
            parts.append(f"{connector}{task}")
        if action:
            connector = " I " if not parts else " "
            parts.append(f"{connector}{action}")
        if result:
            connector = " The result was " if action else " "
            parts.append(f"{connector}{result}")
        
        answer = ''.join(parts)
        
        # Apply length constraints
        sentences = [s.strip() for s in answer.split('.') if s.strip()]
        if len(sentences) > self.config.max_response_sentences:
            answer = '. '.join(sentences[:self.config.max_response_sentences]) + '.'
        
        return answer.strip()
    
    def _format_technical_answer_with_context(self, question: str, context: Dict) -> str:
        """Format technical answer using relevant context"""
        if context["type"] == "project":
            project = context["data"]
            return f"In my {project.get('name', 'recent project')}, I {project.get('description', 'worked with these technologies')}. The key considerations would be {self._extract_technical_insight(question)}."
        elif context["type"] == "skill":
            skill = context["data"]["skill"]
            return f"With my experience in {skill}, I'd approach this by focusing on the core principles and implementation best practices."
        
        return self._generate_generic_technical_answer(question)
    
    def _extract_technical_insight(self, question: str) -> str:
        """Extract relevant technical insights based on question"""
        insights = {
            "performance": "optimization, scalability, and efficient resource usage",
            "design": "modularity, maintainability, and clear separation of concerns", 
            "security": "authentication, authorization, and data protection",
            "database": "normalization, indexing, and query optimization",
            "api": "RESTful design, error handling, and proper status codes"
        }
        
        for key, insight in insights.items():
            if key in question:
                return insight
        
        return "best practices and trade-offs"
    
    def _generate_contextual_behavioral_answer(self, text: str) -> str:
        """Generate behavioral answer using general experience"""
        templates = [
            "In my experience, I focus on understanding the situation first, then developing a structured approach to address the key challenges and measure the results.",
            "I'd start by gathering context and stakeholder input, then create a clear action plan with defined milestones and success metrics.",
            "My approach would involve analyzing the root cause, collaborating with relevant team members, and implementing a solution with measurable outcomes."
        ]
        
        return random.choice(templates)
    
    def _generate_generic_technical_answer(self, text: str) -> str:
        """Enhanced generic technical answer"""
        templates = [
            "I'd approach this by first understanding the requirements and constraints, then evaluating different solutions based on performance, maintainability, and scalability.",
            "The key is to balance functionality with performance while considering long-term maintenance and potential future requirements.",
            "I would focus on the core concepts, evaluate the trade-offs, and choose the approach that best fits the specific use case and constraints."
        ]
        
        return random.choice(templates)
    
    def _generate_general_answer(self, text: str) -> str:
        """Enhanced general answer generation"""
        if "yourself" in text:
            return self._generate_elevator_pitch()
        
        templates = [
            "Based on my background and experience, I would emphasize the importance of clear communication and collaborative problem-solving.",
            "From my perspective, success comes from understanding the bigger picture and aligning individual contributions with team and organizational goals.",
            "I believe in taking a structured approach while remaining flexible and responsive to changing requirements and feedback."
        ]
        
        return random.choice(templates)
    
    def _generate_elevator_pitch(self) -> str:
        """Generate elevator pitch from personal data"""
        if not self.personal_data or not self.personal_data.resume_highlights:
            return "I'm a professional with a strong track record of delivering results through collaborative problem-solving and technical expertise."
        
        highlights = self.personal_data.resume_highlights[:3]  # Top 3 highlights
        return f"I'm a professional with experience in {', '.join(highlights[:2])}. {highlights[2] if len(highlights) > 2 else ''} I focus on delivering measurable results through collaborative problem-solving."
    
    def _format_final_answer(self, answer: str, question_type: QuestionType) -> str:
        """Apply final formatting based on configuration"""
        if not self.config.natural_flow:
            return answer
        
        # Add appropriate intro phrase
        if question_type == QuestionType.BEHAVIORAL:
            intro = random.choice(self.config.behavioral_intro_phrases)
        elif question_type == QuestionType.TECHNICAL:
            intro = random.choice(self.config.technical_intro_phrases)
        else:
            intro = ""
        
        return f"{intro}{answer}".strip()
    
    def _load_default_data(self) -> PersonalData:
        """Load default personal data structure"""
        return PersonalData(
            resume_highlights=[],
            star_stories=[],
            technical_projects=[],
            skills=[],
            experience=[]
        )

# Convenience function for quick usage
def quick_copilot_response(question: str, personal_data: Optional[PersonalData] = None) -> str:
    """Quick function to get a copilot response without setup"""
    copilot = EnhancedInterviewCopilot(personal_data)
    return copilot.process_input(question)
