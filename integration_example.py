#!/usr/bin/env python3
"""
Integration Example: How to integrate the Interview Copilot with different LLM services
and use it in a real interview scenario.
"""

from standalone_interview_copilot import InterviewCopilot, PersonalData


# Example 1: Integration with OpenAI GPT
class OpenAILLMService:
    """Example integration with OpenAI's API."""

    def __init__(self, api_key: str):
        # In a real implementation, you'd import and use the OpenAI client
        self.api_key = api_key

    def generate_response(self, prompt: str) -> str:
        """
        In a real implementation, this would call OpenAI's API.
        For this example, we'll return mock responses.
        """
        # Mock OpenAI-style response
        if "behavioral" in prompt.lower() and "leadership" in prompt.lower():
            return ("When I was leading a team of 5 engineers on a critical project, we faced a major deadline crunch. "
                   "I organized daily stand-ups to track progress, redistributed tasks based on team members' strengths, "
                   "and coordinated with stakeholders to adjust expectations. We delivered the project successfully, "
                   "one day ahead of schedule, and the team felt more cohesive afterward.")

        elif "technical" in prompt.lower() and ("system" in prompt.lower() or "scalable" in prompt.lower()):
            return ("I'd start by analyzing the expected load and user patterns. I'd design a microservices architecture "
                   "using Docker containers for scalability and maintainability. For data storage, I'd use a combination "
                   "of PostgreSQL for transactional data and Redis for caching. I'd implement load balancers and use "
                   "auto-scaling groups in AWS to handle traffic spikes.")

        else:
            return ("Based on my experience with Python and full-stack development, I believe I can contribute "
                   "significantly to your team. I'm particularly excited about the technical challenges this role presents "
                   "and the opportunity to work with cutting-edge technologies.")


# Example 2: Integration with Anthropic Claude
class ClaudeLLMService:
    """Example integration with Anthropic's Claude API."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_response(self, prompt: str) -> str:
        """
        In a real implementation, this would call Anthropic's API.
        """
        # Mock Claude-style response (typically more structured and thoughtful)
        if "behavioral" in prompt.lower():
            return ("I can share an experience from my role as a senior engineer where I had to navigate "
                   "a complex team dynamic. The situation involved two teams with conflicting approaches "
                   "to an API design. I facilitated separate meetings to understand each team's perspective, "
                   "researched industry best practices, and proposed a hybrid solution that addressed both teams' "
                   "core concerns. This resulted in successful project delivery and improved inter-team collaboration.")

        elif "technical" in prompt.lower():
            return ("My approach would focus on understanding the specific requirements first. I'd consider "
                   "factors like expected user volume, data complexity, and performance requirements. "
                   "I'd likely recommend a layered architecture with proper separation of concerns, "
                   "implement comprehensive monitoring and logging, and ensure the system can scale "
                   "horizontally as needed.")

        else:
            return ("I'm drawn to this opportunity because it aligns perfectly with my background in "
                   "building scalable systems and my interest in solving complex technical challenges. "
                   "I believe my experience with cross-functional collaboration and my passion for "
                   "clean, maintainable code would be valuable to your team.")


def setup_professional_data():
    """Set up more realistic professional data."""
    personal_data = PersonalData()

    personal_data.resume_summary = """
    Senior Software Engineer with 6+ years of experience building scalable web applications
    and leading cross-functional teams. Expertise in Python, JavaScript, cloud architecture,
    and DevOps practices. Successfully delivered 15+ production applications serving millions of users.
    """

    personal_data.skills = [
        "Python", "JavaScript", "TypeScript", "React", "Django", "FastAPI",
        "AWS", "Docker", "Kubernetes", "PostgreSQL", "Redis", "MongoDB",
        "GraphQL", "REST APIs", "CI/CD", "Git", "Agile", "Scrum"
    ]

    # Add comprehensive STAR stories
    personal_data.add_star_story(
        title="Scaled system under extreme load",
        situation="Our e-commerce platform was experiencing 300% traffic growth during Black Friday, causing frequent outages and poor user experience.",
        task="I needed to quickly identify bottlenecks and implement solutions to handle the increased load while maintaining system stability.",
        action="I conducted performance profiling, identified database queries as the main bottleneck, implemented query optimization and caching layers using Redis, and set up auto-scaling for our containerized services.",
        result="Reduced response times by 75%, achieved 99.9% uptime during peak traffic, and handled 5x the original load capacity, resulting in 40% increase in sales."
    )

    personal_data.add_star_story(
        title="Led remote team through major refactoring",
        situation="Our codebase had accumulated significant technical debt over 3 years, making new feature development slow and bug-prone, especially challenging with a newly remote team.",
        task="I was asked to lead a 6-person remote team through a major refactoring while maintaining feature velocity and team morale.",
        action="I created a detailed refactoring roadmap, implemented pair programming sessions, set up comprehensive code review processes, and organized weekly technical discussions to share knowledge.",
        result="Successfully refactored 70% of the legacy codebase over 6 months, reduced bug reports by 60%, improved development velocity by 40%, and received positive feedback on team collaboration."
    )

    personal_data.add_star_story(
        title="Resolved critical security vulnerability",
        situation="We discovered a potential data exposure vulnerability in our user authentication system that could affect 100K+ users.",
        task="I needed to quickly assess the impact, implement a fix, and coordinate with stakeholders to manage the security response.",
        action="I immediately assembled a response team, conducted a thorough security audit, implemented additional encryption layers, and coordinated with customer support for transparent communication.",
        result="Patched the vulnerability within 4 hours with zero data compromise, implemented additional security measures, and received recognition from the security team for rapid response."
    )

    # Add relevant projects
    personal_data.add_project(
        name="Real-time Analytics Dashboard",
        description="Built a comprehensive analytics platform for tracking user behavior, sales metrics, and system performance across multiple services",
        technologies="Python, Django, React, PostgreSQL, Redis, Celery, Docker, AWS",
        outcomes="Enabled data-driven decision making, improved response time to issues by 80%, and provided insights that increased user engagement by 25%"
    )

    personal_data.add_project(
        name="Microservices Migration",
        description="Led the architectural migration from a monolithic Django application to a microservices architecture using containerization",
        technologies="Python, Docker, Kubernetes, AWS ECS, PostgreSQL, Redis, GraphQL",
        outcomes="Reduced deployment time from 2 hours to 10 minutes, improved system reliability to 99.9%, and enabled independent team scaling"
    )

    personal_data.add_project(
        name="Machine Learning Recommendation Engine",
        description="Designed and implemented a recommendation system for e-commerce platform using collaborative filtering and content-based approaches",
        technologies="Python, scikit-learn, TensorFlow, Django REST, PostgreSQL, Redis",
        outcomes="Increased user engagement by 35%, improved conversion rates by 22%, and processed 1M+ recommendations daily"
    )

    return personal_data


def demonstrate_interview_scenario():
    """Demonstrate a realistic interview scenario."""
    print("=" * 80)
    print("REALISTIC INTERVIEW COPILOT DEMONSTRATION")
    print("=" * 80)
    print()

    # Set up the copilot with professional data and a mock LLM
    personal_data = setup_professional_data()
    llm_service = OpenAILLMService("your-api-key-here")
    copilot = InterviewCopilot(personal_data, llm_service)

    # Simulate a realistic interview conversation
    interview_segments = [
        # Opening
        "Hi, thanks for joining us today. I'm looking forward to our conversation.",

        # Behavioral questions
        "Tell me about a time when you had to work under extreme pressure.",
        "Describe a situation where you had to lead a team through a difficult challenge.",
        "Can you share an example of a conflict you had with a teammate and how you resolved it?",

        # Technical questions
        "How would you design a system to handle millions of concurrent users?",
        "Walk me through your approach to debugging a performance issue in production.",
        "What's your experience with microservices architecture and when would you recommend it?",

        # General questions
        "Why are you interested in joining our company?",
        "Where do you see yourself in 5 years?",

        # Closing
        "Do you have any questions for me about the role or the company?",
        "Thank you for your time today. We'll be in touch soon."
    ]

    for segment in interview_segments:
        print(f"🎤 INTERVIEWER: \"{segment}\"")

        suggestion = copilot.process_transcribed_text(segment)

        if suggestion == "No suggestion – not a question.":
            print("💭 COPILOT: No suggestion – not a question.")
        else:
            print(f"💡 COPILOT SUGGESTION:")
            print(f"   {suggestion}")

        print("-" * 60)
        print()


def demonstrate_api_integration():
    """Show how to integrate with different LLM APIs."""
    print("=" * 80)
    print("API INTEGRATION EXAMPLES")
    print("=" * 80)
    print()

    personal_data = setup_professional_data()

    # Example with OpenAI
    print("OpenAI Integration:")
    openai_service = OpenAILLMService("your-openai-api-key")
    openai_copilot = InterviewCopilot(personal_data, openai_service)

    question = "Tell me about a time you had to lead a team under pressure."
    response = openai_copilot.process_transcribed_text(question)
    print(f"Question: {question}")
    print(f"Response: {response}")
    print()

    # Example with Claude
    print("Claude Integration:")
    claude_service = ClaudeLLMService("your-anthropic-api-key")
    claude_copilot = InterviewCopilot(personal_data, claude_service)

    response = claude_copilot.process_transcribed_text(question)
    print(f"Question: {question}")
    print(f"Response: {response}")
    print()


def usage_guidelines():
    """Print usage guidelines for the interview copilot."""
    print("=" * 80)
    print("INTERVIEW COPILOT USAGE GUIDELINES")
    print("=" * 80)
    print()

    guidelines = [
        "1. PREPARATION:",
        "   • Set up your PersonalData with resume summary, skills, STAR stories, and projects",
        "   • Choose and configure your preferred LLM service (OpenAI, Anthropic, etc.)",
        "   • Test the system with common interview questions beforehand",
        "",
        "2. DURING THE INTERVIEW:",
        "   • Use speech-to-text to capture interviewer's questions",
        "   • The system will automatically detect questions vs. statements",
        "   • Review suggestions quickly and adapt them to your speaking style",
        "   • Don't rely 100% on suggestions - use your own judgment",
        "",
        "3. BEST PRACTICES:",
        "   • Keep suggestions concise (3-5 sentences as specified)",
        "   • Personalize the suggestions with your own experience",
        "   • Practice common behavioral questions using STAR format",
        "   • Update your personal data regularly with new experiences",
        "",
        "4. ETHICS AND INTEGRITY:",
        "   • Use suggestions as prompts, not scripts",
        "   • Only reference experiences that are genuinely yours",
        "   • Be prepared to elaborate on any story or project you mention",
        "   • Consider disclosing AI assistance if asked directly",
        "",
        "5. TECHNICAL SETUP:",
        "   • Ensure reliable internet connection for LLM API calls",
        "   • Test audio input/speech recognition beforehand",
        "   • Have a backup plan if the system fails during the interview",
        "   • Keep the interface discreet and professional"
    ]

    for guideline in guidelines:
        print(guideline)


if __name__ == "__main__":
    print("Interview Copilot Integration and Usage Examples")
    print()

    # Run all demonstrations
    demonstrate_interview_scenario()
    demonstrate_api_integration()
    usage_guidelines()

    print("\nTo implement this system:")
    print("1. Replace mock LLM services with real API integrations")
    print("2. Add speech-to-text capability for live transcription")
    print("3. Create a user interface for managing personal data")
    print("4. Implement secure storage for API keys and personal information")
    print("5. Add error handling and fallback mechanisms")