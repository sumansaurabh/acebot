#!/usr/bin/env python3
"""Test script for the Interview Copilot functionality."""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from interview_corvus.core.interview_copilot import InterviewCopilot, PersonalData


def setup_sample_data():
    """Set up sample personal data for testing."""
    personal_data = PersonalData()

    # Sample resume summary
    personal_data.resume_summary = """
    Senior Software Engineer with 5+ years of experience in full-stack web development,
    specializing in Python, JavaScript, and cloud technologies. Led multiple cross-functional
    teams and delivered scalable solutions for high-traffic applications.
    """

    # Sample skills
    personal_data.skills = [
        "Python", "JavaScript", "React", "Django", "AWS",
        "Docker", "PostgreSQL", "Redis", "Git", "Agile"
    ]

    # Sample STAR stories
    personal_data.add_star_story(
        title="Led team through critical system migration",
        situation="Our main application was running on legacy infrastructure that was becoming unreliable and expensive to maintain.",
        task="I was tasked with leading a team of 4 engineers to migrate our entire system to AWS while maintaining zero downtime.",
        action="I created a detailed migration plan, set up automated testing, implemented blue-green deployment, and coordinated with stakeholders for gradual rollout.",
        result="Successfully completed the migration 2 weeks ahead of schedule, reduced infrastructure costs by 40%, and improved system reliability from 99.1% to 99.9% uptime."
    )

    personal_data.add_star_story(
        title="Resolved major production conflict between teams",
        situation="Two development teams were in conflict over API design choices, causing project delays and affecting team morale.",
        task="As the senior engineer, I needed to mediate the conflict and find a technical solution that would work for both teams.",
        action="I organized separate meetings with each team to understand their concerns, researched best practices, and proposed a compromise solution with clear documentation.",
        result="Both teams agreed to the new approach, we delivered the project on time, and established better cross-team communication processes."
    )

    # Sample projects
    personal_data.add_project(
        name="E-commerce Analytics Platform",
        description="Built a real-time analytics dashboard for tracking customer behavior and sales metrics",
        technologies="Python, Django, React, PostgreSQL, Redis, AWS",
        outcomes="Improved decision-making speed by 60% and increased sales conversion by 15%"
    )

    personal_data.add_project(
        name="Microservices Migration",
        description="Led the migration from monolithic architecture to microservices",
        technologies="Python, Docker, Kubernetes, AWS ECS, PostgreSQL",
        outcomes="Reduced deployment time from 2 hours to 15 minutes, improved scalability by 300%"
    )

    return personal_data


def test_question_detection():
    """Test the question detection functionality."""
    print("=" * 60)
    print("TESTING QUESTION DETECTION")
    print("=" * 60)

    copilot = InterviewCopilot()

    test_cases = [
        # Questions that should be detected
        "Tell me about a time you faced a difficult challenge.",
        "How do you handle conflict in a team?",
        "What's your greatest strength?",
        "Can you walk me through your experience with Python?",
        "Describe a project you're particularly proud of.",
        "How would you design a scalable system?",

        # Non-questions that should NOT be detected
        "Thank you for joining us today.",
        "Let me tell you about our company culture.",
        "This is a great opportunity for the right candidate.",
        "I see you have experience with React.",
        "We're looking for someone with strong technical skills.",
        "Hello, how are you doing today?",  # Greeting, not interview question
    ]

    for test_text in test_cases:
        result = copilot.question_detector.is_question(test_text)
        print(f"Text: '{test_text}'")
        print(f"Result: {result}")
        print()


def test_interview_responses():
    """Test the full interview copilot responses."""
    print("=" * 60)
    print("TESTING INTERVIEW COPILOT RESPONSES")
    print("=" * 60)

    personal_data = setup_sample_data()
    copilot = InterviewCopilot(personal_data)

    test_questions = [
        # Behavioral questions
        "Tell me about a time you had to lead a team through a difficult situation.",
        "Describe a conflict you had with a coworker and how you resolved it.",
        "What's your biggest professional failure and what did you learn from it?",

        # Technical questions
        "How would you design a scalable web application?",
        "What's your experience with Python and Django?",
        "How do you approach debugging a complex system issue?",

        # General questions
        "Why are you interested in this role?",
        "What are your career goals for the next 5 years?",

        # Non-questions (should return "No suggestion")
        "Thank you for your time today.",
        "Let me tell you about our company.",
        "This interview will take about an hour.",
    ]

    for question in test_questions:
        print(f"INTERVIEWER: '{question}'")
        response = copilot.process_transcribed_text(question)
        print(f"SUGGESTION: {response}")
        print("-" * 50)
        print()


def interactive_demo():
    """Interactive demo where you can input interviewer questions."""
    print("=" * 60)
    print("INTERACTIVE INTERVIEW COPILOT DEMO")
    print("=" * 60)
    print("Enter interviewer questions to get answer suggestions.")
    print("Type 'quit' to exit.")
    print()

    personal_data = setup_sample_data()
    copilot = InterviewCopilot(personal_data)

    while True:
        try:
            question = input("Interviewer says: ").strip()
            if question.lower() in ['quit', 'exit', 'q']:
                break

            if not question:
                continue

            response = copilot.process_transcribed_text(question)
            print(f"Suggestion: {response}")
            print()

        except KeyboardInterrupt:
            print("\nExiting...")
            break


if __name__ == "__main__":
    print("Interview Copilot Test Suite")
    print("=" * 60)

    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_demo()
    else:
        test_question_detection()
        print()
        # Note: The response testing requires LLM access
        print("NOTE: Full response testing requires LLM service configuration.")
        print("To test responses, ensure your API key is configured in the settings.")
        print()
        print("Run with 'python test_interview_copilot.py interactive' for interactive demo.")