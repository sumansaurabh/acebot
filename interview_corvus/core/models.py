"""Pydantic models for structured LLM responses."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class CodeSolution(BaseModel):
    """Structured model for code solution responses."""

    code: str = Field(..., description="Complete code solution")
    language: str = Field(..., description="Programming language of the solution or the question type")
    explanation: str = Field(
        ..., description="Concise explanation of the core solution approach and key logic"
    )
    time_complexity: str = Field(
        ..., description="Time complexity analysis (e.g., O(n), O(log n), etc.)"
    )
    space_complexity: str = Field(..., description="Space complexity analysis")
    edge_cases: List[str] = Field(
        default_factory=list,
        description="List of identified edge cases and how they're handled",
    )
    alternative_approaches: Optional[List[Dict[str, str]]] = Field(
        None,
        description="Alternative approaches with brief descriptions and their time/space complexity",
    )


class McqSolution(BaseModel):
    """Structured model for MCQ solution responses."""

    solution: str = Field(..., description="The list of all questions and the answer and the explanation in markdown format")


class CodeOptimization(BaseModel):
    """Structured model for code optimization responses."""

    original_code: str = Field(..., description="Original code")
    optimized_code: str = Field(..., description="Optimized code")
    language: str = Field(..., description="Programming language of the code")
    improvements: List[str] = Field(
        ..., description="List of improvements made to the code"
    )
    original_time_complexity: str = Field(
        ..., description="Time complexity of the original code"
    )
    optimized_time_complexity: str = Field(
        ..., description="Time complexity of the optimized code"
    )
    original_space_complexity: str = Field(
        ..., description="Space complexity of the original code"
    )
    optimized_space_complexity: str = Field(
        ..., description="Space complexity of the optimized code"
    )
    explanation: str = Field(
        ..., description="Detailed explanation of the optimization process"
    )
