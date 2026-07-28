"""Official Exam Intelligence Parser (M27).

Heuristic PDF analysis only — no LLM, no question-text persistence.
Frozen engines (Decision / QIE / Assessment / Coach / …) are untouched.
"""

from app.services.exam_intelligence.parser.pipeline import ExamIntelligencePipeline

__all__ = ["ExamIntelligencePipeline"]
