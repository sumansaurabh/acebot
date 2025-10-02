# Interview Copilot

An AI-powered interview assistant that helps generate concise, natural answer suggestions during live interviews. The copilot listens to interviewer questions and provides structured, personalized responses based on your background and experience.

## Features

- **Question Detection**: Automatically determines if spoken input is a question
- **Question Classification**: Identifies behavioral, technical, and general question types
- **STAR Method**: Formats behavioral answers using Situation, Task, Action, Result structure
- **Personal Data Integration**: Uses your resume, projects, and STAR stories for relevant responses
- **Natural Language**: Generates answers that sound conversational and authentic
- **Concise Responses**: Limits answers to 3-5 sentences for optimal interview flow

## Quick Start

### Basic Usage

```python
from interview_copilot import InterviewCopilot, PersonalData

# Initialize with your personal data
copilot = InterviewCopilot(personal_data)

# Process interviewer input
response = copilot.process_input("Can you tell me about a time you resolved a conflict?")
print(response)
```

### Example Output

**Input**: `"Can you tell me about a time you resolved a conflict on your team?"`

**Output**: 
*"At Santo Remedio, we faced a conflict between engineering and operations during our Shopify-NetSuite rollout. I needed to resolve the tension and get the project back on track. I set up cross-functional sprint reviews where each team explained blockers openly, then mediated by breaking problems into smaller integration tasks. This reduced tension, gave everyone ownership, and led to a smoother launch with order sync errors dropping by 90% within two weeks."*

## Personal Data Structure

Create a `PersonalData` object with your background information:

```python
personal_data = PersonalData(
    resume_highlights=[
        "Led Shopify-NetSuite integration at Santo Remedio",
        "Reduced order sync errors by 90%",
        "Managed cross-functional teams"
    ],
    star_stories=[
        {
            "situation": "Context of the challenge...",
            "task": "What needed to be accomplished...",
            "action": "Steps I took to address it...",
            "result": "Measurable outcomes achieved...",
            "keywords": ["conflict", "team", "leadership"]
        }
    ],
    technical_projects=[
        {
            "name": "E-commerce Integration",
            "technologies": ["Python", "APIs", "Shopify"],
            "description": "Built automated order sync system"
        }
    ],
    skills=["Python", "System Integration", "Team Leadership"],
    experience=[
        {
            "company": "Santo Remedio",
            "role": "Technical Lead",
            "achievements": ["90% error reduction", "Cross-team collaboration"]
        }
    ]
)
```

## Question Types Handled

### Behavioral Questions
- "Tell me about a time..."
- "Describe a situation when..."
- "Give me an example of..."
- "How did you handle...?"

Uses STAR method formatting with your personal stories.

### Technical Questions
- "What is...?"
- "How does X work?"
- "What's the difference between...?"

Provides structured explanations with implementation details.

### General Questions
- "Tell me about yourself"
- "Why do you want this role?"

Uses your background highlights and experience.

## API Reference

### InterviewCopilot

Main class for processing interview questions and generating responses.

#### Methods

- `__init__(personal_data: PersonalData = None)`: Initialize with optional personal data
- `process_input(transcribed_text: str) -> str`: Main method to process input and generate response

### PersonalData

Data structure for storing personal interview information.

#### Fields

- `resume_highlights: List[str]`: Key achievements and experiences
- `star_stories: List[Dict[str, str]]`: Behavioral interview stories
- `technical_projects: List[Dict[str, str]]`: Technical project details
- `skills: List[str]`: Technical and soft skills
- `experience: List[Dict[str, str]]`: Work experience details

## Running Tests

```bash
python3 interview_copilot.py
```

This will run the built-in test suite with sample questions and display the generated responses.

## Integration Examples

### Live Transcription Integration

```python
# Example with speech-to-text service
import speech_recognition as sr
from interview_copilot import InterviewCopilot

copilot = InterviewCopilot(your_personal_data)
recognizer = sr.Recognizer()

with sr.Microphone() as source:
    audio = recognizer.listen(source)
    transcribed = recognizer.recognize_google(audio)
    suggestion = copilot.process_input(transcribed)
    print(f"Suggestion: {suggestion}")
```

### CLI Tool

```python
# Simple command-line interface
copilot = InterviewCopilot(personal_data)

while True:
    user_input = input("Interviewer: ")
    if user_input.lower() in ['exit', 'quit']:
        break
    
    suggestion = copilot.process_input(user_input)
    print(f"💡 {suggestion}")
```

## Customization

### Adding Custom Question Patterns

```python
copilot = InterviewCopilot(personal_data)

# Add custom behavioral patterns
copilot.question_patterns[QuestionType.BEHAVIORAL].extend([
    r"walk me through",
    r"describe your approach to"
])
```

### Response Length Control

Responses are automatically limited to 3-5 sentences, but you can customize this by modifying the `_format_star_answer` method.

## Best Practices

1. **Prepare Quality STAR Stories**: Include specific, measurable results
2. **Use Relevant Keywords**: Tag stories with keywords for better matching
3. **Practice Natural Delivery**: Use suggestions as starting points, not scripts
4. **Keep It Conversational**: Responses are designed to sound natural when spoken
5. **Test with Real Questions**: Use actual interview questions to validate responses

## Contributing

Feel free to enhance the copilot with:
- Better question classification
- More sophisticated story matching
- Industry-specific question patterns
- Response confidence scoring
- Integration with popular transcription services

## License

MIT License - feel free to use and modify for your interview preparation needs.
