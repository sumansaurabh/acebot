"""
Configuration module for Interview Copilot
Handles settings, patterns, and customizable parameters
"""

from typing import Dict, List
from enum import Enum

class ResponseLength(Enum):
    SHORT = 2  # 1-2 sentences
    MEDIUM = 4  # 3-4 sentences  
    LONG = 6   # 5-6 sentences

class InterviewCopilotConfig:
    """Configuration class for customizing copilot behavior"""
    
    def __init__(self):
        # Response settings
        self.max_response_sentences = 5
        self.min_response_sentences = 3
        self.response_length = ResponseLength.MEDIUM
        
        # Question detection settings
        self.question_confidence_threshold = 0.6
        self.keyword_matching_threshold = 1
        
        # Formatting preferences
        self.use_first_person = True
        self.include_metrics = True
        self.natural_flow = True
        
        # Custom question patterns
        self.custom_behavioral_patterns = []
        self.custom_technical_patterns = []
        
        # Response templates
        self.behavioral_intro_phrases = [
            "Sure — ",
            "Absolutely — ",
            "Great question — ",
            ""
        ]
        
        self.technical_intro_phrases = [
            "That's a good question. ",
            "Let me explain that. ",
            "From my experience, ",
            ""
        ]
    
    def add_behavioral_pattern(self, pattern: str):
        """Add custom behavioral question pattern"""
        self.custom_behavioral_patterns.append(pattern)
    
    def add_technical_pattern(self, pattern: str):
        """Add custom technical question pattern"""
        self.custom_technical_patterns.append(pattern)
    
    def set_response_length(self, length: ResponseLength):
        """Set preferred response length"""
        self.response_length = length
        if length == ResponseLength.SHORT:
            self.max_response_sentences = 2
            self.min_response_sentences = 1
        elif length == ResponseLength.MEDIUM:
            self.max_response_sentences = 4
            self.min_response_sentences = 3
        else:  # LONG
            self.max_response_sentences = 6
            self.min_response_sentences = 5

# Default configuration instance
DEFAULT_CONFIG = InterviewCopilotConfig()

# Industry-specific question patterns
INDUSTRY_PATTERNS = {
    "software_engineering": {
        "behavioral": [
            r"debugging.*process",
            r"code review.*experience",
            r"technical.*decision",
            r"system.*design",
            r"scalability.*challenges"
        ],
        "technical": [
            r"time complexity",
            r"space complexity",
            r"design pattern",
            r"database.*optimization",
            r"api.*design"
        ]
    },
    "product_management": {
        "behavioral": [
            r"product.*launch",
            r"stakeholder.*management", 
            r"feature.*prioritization",
            r"user.*feedback",
            r"roadmap.*planning"
        ],
        "technical": [
            r"metrics.*track",
            r"a/b.*test",
            r"user.*research",
            r"market.*analysis"
        ]
    },
    "data_science": {
        "behavioral": [
            r"data.*project",
            r"model.*performance",
            r"business.*insight",
            r"stakeholder.*results"
        ],
        "technical": [
            r"machine.*learning",
            r"statistical.*method",
            r"feature.*engineering",
            r"model.*validation"
        ]
    }
}

def get_industry_config(industry: str) -> InterviewCopilotConfig:
    """Get configuration tailored for specific industry"""
    config = InterviewCopilotConfig()
    
    if industry in INDUSTRY_PATTERNS:
        patterns = INDUSTRY_PATTERNS[industry]
        config.custom_behavioral_patterns = patterns.get("behavioral", [])
        config.custom_technical_patterns = patterns.get("technical", [])
    
    return config
