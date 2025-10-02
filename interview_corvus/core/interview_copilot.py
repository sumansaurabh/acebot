"""Interview Copilot for real-time answer suggestions during live interviews."""

import re
from typing import Dict, List, Optional, Union
from interview_corvus.core.llm_service import LLMService
from interview_corvus.core.prompt_manager import PromptManager
from interview_corvus.config import settings


class PersonalData:
    """Container for personal interview data."""

    def __init__(self):
        self.resume_summary: str = ""
        self.star_stories: List[Dict[str, str]] = []
        self.projects: List[Dict[str, str]] = []
        self.skills: List[str] = []

    def add_star_story(self, title: str, situation: str, task: str, action: str, result: str):
        """Add a STAR story to the personal data."""
        self.star_stories.append({
            "title": title,
            "situation": situation,
            "task": task,
            "action": action,
            "result": result
        })

    def add_project(self, name: str, description: str, technologies: str, outcomes: str):
        """Add a project to the personal data."""
        self.projects.append({
            "name": name,
            "description": description,
            "technologies": technologies,
            "outcomes": outcomes
        })


class QuestionDetector:
    """Detects if a text segment is a question requiring an answer."""

    def __init__(self):
        # Question indicators
        self.question_words = {
            'what', 'how', 'why', 'when', 'where', 'who', 'which', 'whose',
            'can', 'could', 'would', 'should', 'do', 'does', 'did', 'are', 'is',
            'have', 'has', 'will', 'tell', 'describe', 'explain', 'walk'
        }

        # Behavioral question patterns
        self.behavioral_patterns = [
            r'\b(tell me about|describe|give me an example)',
            r'\b(time when|situation where|experience with)',
            r'\b(how do you|how would you|what would you do)',
            r'\b(challenge|conflict|difficult|problem)',
            r'\b(leadership|teamwork|collaboration)',
            r'\b(failure|mistake|learned|growth)'
        ]

        # Technical question patterns
        self.technical_patterns = [
            r'\b(how does|how would|what is|what are)',
            r'\b(implement|design|solve|optimize)',
            r'\b(algorithm|data structure|database|system)',
            r'\b(complexity|performance|scalability)'
        ]

    def is_question(self, text: str) -> Dict[str, Union[bool, str]]:
        """
        Determine if the text is a question and classify its type.

        Returns:
            dict: {
                'is_question': bool,
                'question_type': str,  # 'behavioral', 'technical', 'general'
                'confidence': float
            }
        """
        if not text or len(text.strip()) < 3:
            return {'is_question': False, 'question_type': 'none', 'confidence': 0.0}

        text_lower = text.lower().strip()

        # Check for question mark
        has_question_mark = text.strip().endswith('?')

        # Check for question words at the beginning
        words = text_lower.split()
        starts_with_question_word = len(words) > 0 and words[0] in self.question_words

        # Check for behavioral patterns
        behavioral_match = any(re.search(pattern, text_lower) for pattern in self.behavioral_patterns)

        # Check for technical patterns
        technical_match = any(re.search(pattern, text_lower) for pattern in self.technical_patterns)

        # Calculate confidence and determine type
        confidence = 0.0
        question_type = 'none'

        if has_question_mark:
            confidence += 0.4
        if starts_with_question_word:
            confidence += 0.3

        if behavioral_match:
            confidence += 0.4
            question_type = 'behavioral'
        elif technical_match:
            confidence += 0.4
            question_type = 'technical'
        elif starts_with_question_word or has_question_mark:
            question_type = 'general'
            confidence += 0.2

        # Additional patterns that suggest questions
        question_patterns = [
            r'\btell me\b',
            r'\bwalk me through\b',
            r'\bexplain\b',
            r'\bwhat\'s your\b',
            r'\bhow\'s your\b'
        ]

        if any(re.search(pattern, text_lower) for pattern in question_patterns):
            confidence += 0.2
            if question_type == 'none':
                question_type = 'general'

        is_question = confidence >= 0.5

        return {
            'is_question': is_question,
            'question_type': question_type if is_question else 'none',
            'confidence': min(confidence, 1.0)
        }


class InterviewCopilot:
    """Main interview copilot class for generating answer suggestions."""

    def __init__(self, personal_data: Optional[PersonalData] = None):
        self.llm_service = LLMService()
        self.prompt_manager = PromptManager()
        self.question_detector = QuestionDetector()
        self.personal_data = personal_data or PersonalData()

        # Add copilot-specific prompt templates
        self._initialize_copilot_prompts()

    def _initialize_copilot_prompts(self):
        """Initialize prompt templates for the interview copilot."""
        copilot_templates = {
            "behavioral_answer": """
You are an interview copilot helping a candidate answer behavioral interview questions.

QUESTION: {question}

PERSONAL CONTEXT:
Resume Summary: {resume_summary}
Relevant STAR Stories: {star_stories}
Relevant Projects: {projects}

INSTRUCTIONS:
1. Generate a concise, natural answer suggestion (3-5 sentences)
2. Use STAR format: Situation, Task, Action, Result
3. Draw from the provided personal context when relevant
4. Make it sound conversational, like something the candidate would say
5. Keep it brief but impactful

ANSWER SUGGESTION:
""",

            "technical_answer": """
You are an interview copilot helping a candidate answer technical interview questions.

QUESTION: {question}

PERSONAL CONTEXT:
Technical Skills: {skills}
Relevant Projects: {projects}
Resume Summary: {resume_summary}

INSTRUCTIONS:
1. Generate a clear, structured answer (3-5 sentences)
2. Be direct and technical but not overly complex
3. Reference relevant experience from personal context if applicable
4. Sound natural and conversational
5. Focus on demonstrating knowledge and problem-solving approach

ANSWER SUGGESTION:
""",

            "general_answer": """
You are an interview copilot helping a candidate answer general interview questions.

QUESTION: {question}

PERSONAL CONTEXT:
Resume Summary: {resume_summary}
Skills: {skills}
Projects: {projects}

INSTRUCTIONS:
1. Generate a concise, professional answer (3-5 sentences)
2. Draw from personal context when relevant
3. Sound natural and conversational
4. Be honest and authentic
5. Keep it focused and to the point

ANSWER SUGGESTION:
""",

            "question_classifier": """
Analyze this transcribed text and determine if it's a question requiring an answer:

TEXT: "{text}"

Respond with ONLY one of these exact phrases:
- "No suggestion – not a question."
- "QUESTION_DETECTED"

If it's clearly a question, respond with "QUESTION_DETECTED"
If it's a statement, greeting, comment, or unclear, respond with "No suggestion – not a question."
"""
        }

        for name, template in copilot_templates.items():
            self.prompt_manager.add_custom_template(name, template)

    def process_transcribed_text(self, transcribed_text: str) -> str:
        """
        Main method to process transcribed text and generate answer suggestions.

        Args:
            transcribed_text: The interviewer's spoken segment

        Returns:
            str: Either "No suggestion – not a question." or an answer suggestion
        """
        if not transcribed_text or not transcribed_text.strip():
            return "No suggestion – not a question."

        # Detect if it's a question
        question_analysis = self.question_detector.is_question(transcribed_text)

        if not question_analysis['is_question']:
            return "No suggestion – not a question."

        # Generate answer suggestion based on question type
        question_type = question_analysis['question_type']

        try:
            if question_type == 'behavioral':
                return self._generate_behavioral_answer(transcribed_text)
            elif question_type == 'technical':
                return self._generate_technical_answer(transcribed_text)
            else:
                return self._generate_general_answer(transcribed_text)

        except Exception as e:
            # Fallback in case of error
            return f"Error generating suggestion: {str(e)}"

    def _generate_behavioral_answer(self, question: str) -> str:
        """Generate answer for behavioral questions using STAR format."""
        # Find relevant STAR stories
        relevant_stories = self._find_relevant_stories(question)
        stories_text = self._format_star_stories(relevant_stories[:2])  # Use top 2 relevant stories

        # Find relevant projects
        relevant_projects = self._find_relevant_projects(question)
        projects_text = self._format_projects(relevant_projects[:2])

        prompt = self.prompt_manager.get_prompt(
            "behavioral_answer",
            question=question,
            resume_summary=self.personal_data.resume_summary,
            star_stories=stories_text,
            projects=projects_text
        )

        response = self.llm_service.generate_response(prompt)
        return self._clean_response(response)

    def _generate_technical_answer(self, question: str) -> str:
        """Generate answer for technical questions."""
        relevant_projects = self._find_relevant_projects(question)
        projects_text = self._format_projects(relevant_projects[:2])
        skills_text = ", ".join(self.personal_data.skills)

        prompt = self.prompt_manager.get_prompt(
            "technical_answer",
            question=question,
            skills=skills_text,
            projects=projects_text,
            resume_summary=self.personal_data.resume_summary
        )

        response = self.llm_service.generate_response(prompt)
        return self._clean_response(response)

    def _generate_general_answer(self, question: str) -> str:
        """Generate answer for general questions."""
        relevant_projects = self._find_relevant_projects(question)
        projects_text = self._format_projects(relevant_projects[:1])
        skills_text = ", ".join(self.personal_data.skills[:5])  # Top 5 skills

        prompt = self.prompt_manager.get_prompt(
            "general_answer",
            question=question,
            resume_summary=self.personal_data.resume_summary,
            skills=skills_text,
            projects=projects_text
        )

        response = self.llm_service.generate_response(prompt)
        return self._clean_response(response)

    def _find_relevant_stories(self, question: str) -> List[Dict[str, str]]:
        """Find STAR stories relevant to the question."""
        question_lower = question.lower()
        scored_stories = []

        keywords_map = {
            'leadership': ['leadership', 'lead', 'managed', 'team', 'mentor'],
            'challenge': ['challenge', 'difficult', 'problem', 'obstacle', 'conflict'],
            'teamwork': ['teamwork', 'collaboration', 'team', 'group', 'together'],
            'failure': ['failure', 'mistake', 'wrong', 'failed', 'learn'],
            'success': ['success', 'achievement', 'accomplished', 'delivered']
        }

        for story in self.personal_data.star_stories:
            score = 0
            story_text = f"{story.get('title', '')} {story.get('situation', '')} {story.get('action', '')}".lower()

            # Score based on keyword matches
            for category, keywords in keywords_map.items():
                if any(keyword in question_lower for keyword in keywords):
                    if any(keyword in story_text for keyword in keywords):
                        score += 2
                    if category in story.get('title', '').lower():
                        score += 1

            if score > 0:
                scored_stories.append((score, story))

        # Return stories sorted by relevance score
        scored_stories.sort(key=lambda x: x[0], reverse=True)
        return [story for _, story in scored_stories]

    def _find_relevant_projects(self, question: str) -> List[Dict[str, str]]:
        """Find projects relevant to the question."""
        question_lower = question.lower()
        scored_projects = []

        for project in self.personal_data.projects:
            score = 0
            project_text = f"{project.get('name', '')} {project.get('description', '')} {project.get('technologies', '')}".lower()

            # Simple keyword matching
            common_words = set(question_lower.split()) & set(project_text.split())
            score = len(common_words)

            if score > 0:
                scored_projects.append((score, project))

        scored_projects.sort(key=lambda x: x[0], reverse=True)
        return [project for _, project in scored_projects]

    def _format_star_stories(self, stories: List[Dict[str, str]]) -> str:
        """Format STAR stories for prompt inclusion."""
        if not stories:
            return "No relevant STAR stories available."

        formatted = []
        for i, story in enumerate(stories, 1):
            formatted.append(f"Story {i}: {story.get('title', 'Untitled')}")
            formatted.append(f"Situation: {story.get('situation', '')}")
            formatted.append(f"Task: {story.get('task', '')}")
            formatted.append(f"Action: {story.get('action', '')}")
            formatted.append(f"Result: {story.get('result', '')}")
            formatted.append("")

        return "\n".join(formatted)

    def _format_projects(self, projects: List[Dict[str, str]]) -> str:
        """Format projects for prompt inclusion."""
        if not projects:
            return "No relevant projects available."

        formatted = []
        for i, project in enumerate(projects, 1):
            formatted.append(f"Project {i}: {project.get('name', 'Untitled')}")
            formatted.append(f"Description: {project.get('description', '')}")
            formatted.append(f"Technologies: {project.get('technologies', '')}")
            formatted.append(f"Outcomes: {project.get('outcomes', '')}")
            formatted.append("")

        return "\n".join(formatted)

    def _clean_response(self, response: str) -> str:
        """Clean and format the AI response for presentation."""
        if not response:
            return "Unable to generate suggestion."

        # Remove common AI response prefixes
        prefixes_to_remove = [
            "Here's a suggested answer:",
            "Answer suggestion:",
            "I would suggest:",
            "You could say:",
            "Consider this response:"
        ]

        for prefix in prefixes_to_remove:
            if response.strip().lower().startswith(prefix.lower()):
                response = response[len(prefix):].strip()

        # Clean up formatting
        response = response.strip()

        # Ensure it doesn't start with quotes
        if response.startswith('"') and response.endswith('"'):
            response = response[1:-1]

        return response