"""
Interview Copilot - AI-powered interview assistant
Helps generate concise, natural answer suggestions during live interviews
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

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

@dataclass
class STARStory:
    """STAR format story structure"""
    situation: str
    task: str
    action: str
    result: str
    keywords: List[str]  # For matching relevant stories

class InterviewCopilot:
    """Main copilot class for generating interview answer suggestions"""
    
    def __init__(self, personal_data: Optional[PersonalData] = None):
        self.personal_data = personal_data or self._load_default_data()
        self.question_patterns = self._initialize_question_patterns()
    
    def _initialize_question_patterns(self) -> Dict[QuestionType, List[str]]:
        """Initialize regex patterns for question type detection"""
        return {
            QuestionType.BEHAVIORAL: [
                r"tell me about a time",
                r"describe a situation",
                r"give me an example",
                r"when have you",
                r"how did you handle",
                r"what would you do if",
                r"describe your experience with"
            ],
            QuestionType.TECHNICAL: [
                r"what is",
                r"how does.*work",
                r"explain.*algorithm",
                r"what's the difference between",
                r"how would you implement",
                r"what are the pros and cons"
            ]
        }
    
    def process_input(self, transcribed_text: str) -> str:
        """
        Main processing function - determines if input is a question and generates response
        """
        # Clean and normalize input
        text = self._clean_text(transcribed_text)
        
        # Check if it's a question
        if not self._is_question(text):
            return "No suggestion – not a question."
        
        # Determine question type
        question_type = self._classify_question(text)
        
        # Generate answer suggestion
        answer = self._generate_answer(text, question_type)
        
        return answer
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize the transcribed text"""
        return text.strip().lower()
    
    def _is_question(self, text: str) -> bool:
        """Determine if the text is a question"""
        question_indicators = [
            text.endswith('?'),
            text.startswith(('what', 'how', 'why', 'when', 'where', 'who')),
            text.startswith(('can you', 'could you', 'would you', 'do you')),
            text.startswith(('tell me', 'describe', 'explain')),
            'tell me about' in text,
            'give me an example' in text
        ]
        return any(question_indicators)
    
    def _classify_question(self, text: str) -> QuestionType:
        """Classify the type of question"""
        for question_type, patterns in self.question_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return question_type
        return QuestionType.GENERAL
    
    def _generate_answer(self, text: str, question_type: QuestionType) -> str:
        """Generate answer suggestion based on question type"""
        if question_type == QuestionType.BEHAVIORAL:
            return self._generate_behavioral_answer(text)
        elif question_type == QuestionType.TECHNICAL:
            return self._generate_technical_answer(text)
        else:
            return self._generate_general_answer(text)
    
    def _generate_behavioral_answer(self, text: str) -> str:
        """Generate STAR-formatted behavioral answer"""
        # Find relevant STAR story
        relevant_story = self._find_relevant_story(text)
        
        if relevant_story:
            return self._format_star_answer(relevant_story)
        else:
            # Generate generic STAR structure
            return self._generate_generic_behavioral_answer(text)
    
    def _generate_technical_answer(self, text: str) -> str:
        """Generate structured technical answer"""
        # This would integrate with technical knowledge base
        return "I'd approach this by first understanding the core concept, then explaining the implementation details and trade-offs involved."
    
    def _generate_general_answer(self, text: str) -> str:
        """Generate general interview answer"""
        return "Based on my experience, I would focus on the key principles and provide a specific example from my background."
    
    def _find_relevant_story(self, text: str) -> Optional[Dict[str, str]]:
        """Find the most relevant STAR story for the question"""
        if not self.personal_data or not self.personal_data.star_stories:
            return None
        
        # Simple keyword matching - could be enhanced with NLP
        question_keywords = text.split()
        best_story = None
        best_score = 0
        
        for story in self.personal_data.star_stories:
            score = 0
            # Handle both string values and lists in story data
            story_parts = []
            for value in story.values():
                if isinstance(value, list):
                    story_parts.extend(value)
                else:
                    story_parts.append(str(value))
            story_text = ' '.join(story_parts).lower()
            
            for keyword in question_keywords:
                if keyword in story_text:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_story = story
        
        return best_story if best_score > 0 else None
    
    def _format_star_answer(self, story: Dict[str, str]) -> str:
        """Format a STAR story into a natural answer"""
        situation = story.get('situation', '')
        task = story.get('task', '')
        action = story.get('action', '')
        result = story.get('result', '')
        
        # Create natural flow
        answer = f"{situation} {task} {action} {result}"
        
        # Limit to 3-5 sentences
        sentences = answer.split('. ')
        if len(sentences) > 5:
            answer = '. '.join(sentences[:5]) + '.'
        
        return answer.strip()
    
    def _generate_generic_behavioral_answer(self, text: str) -> str:
        """Generate a generic behavioral answer structure"""
        return ("I'd start by setting the context of the situation, then explain the specific challenge or task I needed to address, "
                "walk through the concrete actions I took, and conclude with the measurable results achieved.")
    
    def _load_default_data(self) -> PersonalData:
        """Load default personal data structure"""
        return PersonalData(
            resume_highlights=[],
            star_stories=[],
            technical_projects=[],
            skills=[],
            experience=[]
        )

# Example usage and testing
def main():
    """Example usage of the Interview Copilot"""
    
    # Sample personal data
    sample_data = PersonalData(
        resume_highlights=[
            "Led Shopify-NetSuite integration at Santo Remedio",
            "Reduced order sync errors by 90%",
            "Managed cross-functional teams"
        ],
        star_stories=[
            {
                "situation": "At Santo Remedio, we faced a conflict between engineering and operations during our Shopify-NetSuite rollout.",
                "task": "I needed to resolve the tension and get the project back on track.",
                "action": "I set up cross-functional sprint reviews where each team explained blockers openly, then mediated by breaking problems into smaller integration tasks.",
                "result": "This reduced tension, gave everyone ownership, and led to a smoother launch with order sync errors dropping by 90% within two weeks.",
                "keywords": ["conflict", "team", "integration", "mediation"]
            }
        ],
        technical_projects=[],
        skills=["Python", "System Integration", "Team Leadership"],
        experience=[]
    )
    
    # Initialize copilot
    copilot = InterviewCopilot(sample_data)
    
    # Test cases
    test_inputs = [
        "Can you tell me about a time you resolved a conflict on your team?",
        "What is your experience with Python?",
        "The weather is nice today.",
        "How do you handle difficult stakeholders?",
        "Tell me about yourself."
    ]
    
    print("=== Interview Copilot Test Results ===\n")
    
    for i, test_input in enumerate(test_inputs, 1):
        print(f"Test {i}: {test_input}")
        result = copilot.process_input(test_input)
        print(f"Response: {result}")
        print("-" * 50)

if __name__ == "__main__":
    main()
