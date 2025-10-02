# Interview Copilot Test Suite

import unittest
from unittest.mock import patch
import json
import tempfile
import os

from enhanced_copilot import EnhancedInterviewCopilot, PersonalData
from config import InterviewCopilotConfig, ResponseLength

class TestInterviewCopilot(unittest.TestCase):
    """Test suite for Interview Copilot functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.sample_data = PersonalData(
            resume_highlights=[
                "Led Shopify-NetSuite integration",
                "Reduced errors by 90%",
                "Managed cross-functional teams"
            ],
            star_stories=[
                {
                    "situation": "Team conflict during integration project",
                    "task": "Resolve tension and deliver on time",
                    "action": "Set up cross-functional reviews and mediation",
                    "result": "90% error reduction and successful launch",
                    "keywords": ["conflict", "team", "leadership", "integration"]
                },
                {
                    "situation": "Performance issues in e-commerce platform",
                    "task": "Improve checkout speed",
                    "action": "Implemented caching and database optimization",
                    "result": "60% speed improvement and $200K revenue increase",
                    "keywords": ["performance", "optimization", "technical"]
                }
            ],
            technical_projects=[
                {
                    "name": "E-commerce Platform",
                    "technologies": ["Python", "Django", "PostgreSQL"],
                    "description": "Built automated order sync system"
                }
            ],
            skills=["Python", "Leadership", "System Integration"],
            experience=[]
        )
        
        self.copilot = EnhancedInterviewCopilot(self.sample_data)
    
    def test_question_detection(self):
        """Test question detection functionality"""
        # True questions
        questions = [
            "Can you tell me about a time?",
            "What is your experience with Python?",
            "How do you handle conflicts?",
            "Describe a situation when...",
            "Tell me about yourself."
        ]
        
        for question in questions:
            with self.subTest(question=question):
                result = self.copilot.process_input(question)
                self.assertNotEqual(result, "No suggestion – not a question.")
        
        # Not questions
        non_questions = [
            "The weather is nice today.",
            "I see you have Python experience.",
            "Great, thanks for that answer."
        ]
        
        for non_question in non_questions:
            with self.subTest(non_question=non_question):
                result = self.copilot.process_input(non_question)
                self.assertEqual(result, "No suggestion – not a question.")
    
    def test_behavioral_question_matching(self):
        """Test behavioral question story matching"""
        conflict_question = "Tell me about a time you resolved a conflict"
        result = self.copilot.process_input(conflict_question)
        
        self.assertIn("Team conflict", result)
        self.assertIn("cross-functional", result)
        self.assertNotEqual(result, "No suggestion – not a question.")
    
    def test_technical_question_handling(self):
        """Test technical question responses"""
        tech_question = "What is your experience with Python?"
        result = self.copilot.process_input(tech_question)
        
        self.assertNotEqual(result, "No suggestion – not a question.")
        self.assertTrue(len(result.split()) > 5)  # Should be substantial response
    
    def test_star_format(self):
        """Test STAR format in responses"""
        behavioral_question = "Give me an example of when you improved performance"
        result = self.copilot.process_input(behavioral_question)
        
        # Should contain elements of STAR format
        result_lower = result.lower()
        self.assertTrue(any(keyword in result_lower for keyword in 
                          ["performance", "optimization", "implemented", "result"]))
    
    def test_response_length_control(self):
        """Test response length configuration"""
        config = InterviewCopilotConfig()
        config.set_response_length(ResponseLength.SHORT)
        
        short_copilot = EnhancedInterviewCopilot(self.sample_data, config)
        
        question = "Tell me about a time you solved a problem"
        result = short_copilot.process_input(question)
        
        sentences = [s.strip() for s in result.split('.') if s.strip()]
        self.assertLessEqual(len(sentences), 2)  # Short responses should be 1-2 sentences
    
    def test_keyword_matching(self):
        """Test keyword matching for story selection"""
        # Question with performance keywords should match performance story
        performance_question = "How do you handle performance issues?"
        result = self.copilot.process_input(performance_question)
        
        self.assertTrue(any(keyword in result.lower() for keyword in 
                          ["performance", "optimization", "caching"]))
    
    def test_custom_patterns(self):
        """Test custom question patterns"""
        config = InterviewCopilotConfig()
        config.add_behavioral_pattern(r"walk me through.*challenge")
        
        custom_copilot = EnhancedInterviewCopilot(self.sample_data, config)
        
        custom_question = "Walk me through a challenge you faced"
        result = custom_copilot.process_input(custom_question)
        
        self.assertNotEqual(result, "No suggestion – not a question.")

class TestPersonalDataLoading(unittest.TestCase):
    """Test personal data loading from JSON"""
    
    def test_json_data_loading(self):
        """Test loading personal data from JSON file"""
        sample_data = {
            "resume_highlights": ["Achievement 1", "Achievement 2"],
            "star_stories": [
                {
                    "situation": "Test situation",
                    "task": "Test task",
                    "action": "Test action", 
                    "result": "Test result"
                }
            ],
            "technical_projects": [],
            "skills": ["Python", "Testing"],
            "experience": []
        }
        
        # Create temporary JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_data, f)
            temp_path = f.name
        
        try:
            # Load data from CLI module
            from cli import load_personal_data
            loaded_data = load_personal_data(temp_path)
            
            self.assertIsNotNone(loaded_data)
            self.assertEqual(loaded_data.resume_highlights, sample_data["resume_highlights"])
            self.assertEqual(loaded_data.skills, sample_data["skills"])
            self.assertEqual(len(loaded_data.star_stories), 1)
        
        finally:
            os.unlink(temp_path)

class TestConfigurationSystem(unittest.TestCase):
    """Test configuration system"""
    
    def test_response_length_settings(self):
        """Test response length configuration"""
        config = InterviewCopilotConfig()
        
        # Test short setting
        config.set_response_length(ResponseLength.SHORT)
        self.assertEqual(config.max_response_sentences, 2)
        self.assertEqual(config.min_response_sentences, 1)
        
        # Test long setting
        config.set_response_length(ResponseLength.LONG)
        self.assertEqual(config.max_response_sentences, 6)
        self.assertEqual(config.min_response_sentences, 5)
    
    def test_industry_specific_patterns(self):
        """Test industry-specific configurations"""
        from config import get_industry_config
        
        software_config = get_industry_config("software_engineering")
        self.assertTrue(len(software_config.custom_behavioral_patterns) > 0)
        self.assertTrue(len(software_config.custom_technical_patterns) > 0)

def run_tests():
    """Run all tests"""
    unittest.main(verbosity=2)

if __name__ == '__main__':
    run_tests()
