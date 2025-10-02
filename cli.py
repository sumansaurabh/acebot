#!/usr/bin/env python3
"""
CLI tool for Interview Copilot
Usage: python cli.py [options]
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from enhanced_copilot import EnhancedInterviewCopilot, PersonalData, QuestionType
from config import InterviewCopilotConfig, get_industry_config

def load_personal_data(file_path: str) -> Optional[PersonalData]:
    """Load personal data from JSON file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return PersonalData(
            resume_highlights=data.get('resume_highlights', []),
            star_stories=data.get('star_stories', []),
            technical_projects=data.get('technical_projects', []),
            skills=data.get('skills', []),
            experience=data.get('experience', [])
        )
    except Exception as e:
        print(f"Error loading personal data: {e}")
        return None

def create_sample_data_file(file_path: str):
    """Create a sample personal data file"""
    sample_data = {
        "resume_highlights": [
            "Led Shopify-NetSuite integration at Santo Remedio",
            "Reduced order sync errors by 90%",
            "Managed cross-functional teams of 8+ people"
        ],
        "star_stories": [
            {
                "situation": "At Santo Remedio, we faced a conflict between engineering and operations during our Shopify-NetSuite rollout.",
                "task": "I needed to resolve the tension and get the project back on track within two weeks.",
                "action": "I set up cross-functional sprint reviews where each team explained blockers openly, then mediated by breaking problems into smaller integration tasks with clear ownership.",
                "result": "This reduced tension, gave everyone ownership, and led to a smoother launch with order sync errors dropping by 90% within two weeks.",
                "keywords": ["conflict", "team", "integration", "mediation", "leadership"]
            },
            {
                "situation": "Our e-commerce platform was experiencing 30% cart abandonment due to slow checkout performance.",
                "task": "I was tasked with improving checkout speed and reducing abandonment rates.",
                "action": "I implemented database query optimization, added Redis caching, and streamlined the payment flow by removing unnecessary form fields.",
                "result": "Checkout time decreased by 60% and cart abandonment dropped to 18%, resulting in $200K additional monthly revenue.",
                "keywords": ["performance", "optimization", "e-commerce", "technical", "results"]
            }
        ],
        "technical_projects": [
            {
                "name": "E-commerce Integration Platform",
                "technologies": ["Python", "Django", "PostgreSQL", "Redis", "API Integration"],
                "description": "Built automated order sync system connecting Shopify with NetSuite ERP",
                "impact": "Reduced manual processing time by 80% and eliminated data sync errors"
            }
        ],
        "skills": [
            "Python", "System Integration", "Team Leadership", "API Design", 
            "Database Optimization", "Cross-functional Collaboration"
        ],
        "experience": [
            {
                "company": "Santo Remedio",
                "role": "Technical Lead",
                "duration": "2022-2024",
                "achievements": [
                    "90% error reduction in order processing",
                    "Led team of 8 engineers and operations staff",
                    "$200K monthly revenue increase through performance improvements"
                ]
            }
        ]
    }
    
    with open(file_path, 'w') as f:
        json.dump(sample_data, f, indent=2)
    
    print(f"Sample data file created: {file_path}")
    print("Edit this file with your personal information before using the copilot.")

def interactive_mode(copilot: EnhancedInterviewCopilot):
    """Run interactive CLI mode"""
    print("\n🎤 Interview Copilot - Interactive Mode")
    print("=" * 50)
    print("Enter interviewer questions below. Type 'quit' or 'exit' to stop.")
    print("Type 'help' for available commands.\n")
    
    while True:
        try:
            user_input = input("\nInterviewer: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Good luck with your interview!")
                break
            
            if user_input.lower() in ['help', 'h']:
                print("\nAvailable commands:")
                print("  help, h     - Show this help message")
                print("  quit, exit  - Exit the copilot")
                print("  clear       - Clear the screen")
                print("\nJust type any interviewer question to get a suggestion!")
                continue
            
            if user_input.lower() == 'clear':
                print("\033[H\033[J", end="")  # Clear screen
                continue
            
            # Process the question
            response = copilot.process_input(user_input)
            
            if response == "No suggestion – not a question.":
                print(f"\n💭 {response}")
            else:
                print(f"\n💡 Suggestion:")
                print(f"   {response}")
                
        except KeyboardInterrupt:
            print("\n\n👋 Good luck with your interview!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

def batch_mode(copilot: EnhancedInterviewCopilot, questions: list):
    """Process questions in batch mode"""
    print("\n🎤 Interview Copilot - Batch Processing")
    print("=" * 50)
    
    for i, question in enumerate(questions, 1):
        print(f"\nQuestion {i}: {question}")
        response = copilot.process_input(question)
        print(f"Response: {response}")
        print("-" * 30)

def main():
    parser = argparse.ArgumentParser(description='Interview Copilot CLI')
    parser.add_argument('--data', '-d', type=str, 
                       help='Path to personal data JSON file')
    parser.add_argument('--industry', '-i', type=str,
                       choices=['software_engineering', 'product_management', 'data_science'],
                       help='Industry-specific configuration')
    parser.add_argument('--create-sample', action='store_true',
                       help='Create sample data file')
    parser.add_argument('--batch', '-b', nargs='+',
                       help='Process questions in batch mode')
    parser.add_argument('--length', choices=['short', 'medium', 'long'], 
                       default='medium', help='Response length preference')
    
    args = parser.parse_args()
    
    # Create sample data file if requested
    if args.create_sample:
        sample_path = 'personal_data_sample.json'
        create_sample_data_file(sample_path)
        return
    
    # Load personal data
    personal_data = None
    if args.data:
        if not Path(args.data).exists():
            print(f"❌ Data file not found: {args.data}")
            print("Use --create-sample to generate a sample file.")
            return
        personal_data = load_personal_data(args.data)
        if personal_data is None:
            return
        print(f"✅ Loaded personal data from {args.data}")
    else:
        print("⚠️  No personal data loaded. Using generic responses.")
        print("Use --create-sample to generate a data file, then --data <file> to load it.")
    
    # Configure copilot
    if args.industry:
        config = get_industry_config(args.industry)
        print(f"✅ Using {args.industry} industry configuration")
    else:
        config = InterviewCopilotConfig()
    
    # Set response length
    from config import ResponseLength
    length_map = {
        'short': ResponseLength.SHORT,
        'medium': ResponseLength.MEDIUM, 
        'long': ResponseLength.LONG
    }
    config.set_response_length(length_map[args.length])
    
    # Initialize copilot
    copilot = EnhancedInterviewCopilot(personal_data, config)
    
    # Run in appropriate mode
    if args.batch:
        batch_mode(copilot, args.batch)
    else:
        interactive_mode(copilot)

if __name__ == '__main__':
    main()
