"""Combine retrieved sections into a response."""

from __future__ import annotations

from dataclasses import dataclass
import re
import uuid

from backend.src.providers.llm_provider import ChatProvider, StubProvider


@dataclass
class AnswerResult:
    """Structured result returned by the answer service."""

    response_id: str
    generated_text: str
    is_fallback: bool = False
    clarification_required: bool = False


class AnswerService:
    def __init__(
        self,
        provider: ChatProvider | None = None,
        *,
    min_context_chars: int = 80,
    ) -> None:
        self.provider = provider or StubProvider()
        self.min_context_chars = min_context_chars

    def is_ambiguous(self, question: str) -> bool:
        """
        Detect if a query is ambiguous based on simple heuristics.
        
        A query is considered ambiguous if:
        - It's very short (1-2 words)
        - Contains only common words
        - Lacks specific technical terms or context
        
        Returns:
            True if the query appears ambiguous, False otherwise
        """
        # Normalize and tokenize
        words = question.strip().lower().split()
        
        # Very short queries are often ambiguous
        if len(words) <= 2:
            return True
        
        # Common question words that need more context
        vague_patterns = [
            r'\bhow\b',
            r'\bwhat\b',
            r'\bwhen\b',
            r'\bwhere\b',
            r'\bwhy\b',
            r'\btell me about\b',
            r'\bexplain\b',
        ]
        
        # Check if query is only vague question words
        question_lower = question.lower()
        has_vague_word = any(re.search(pattern, question_lower) for pattern in vague_patterns)
        
        # If it's a vague question with few words and no specific terms, it's ambiguous
        if has_vague_word and len(words) <= 4:
            # Check if there's at least one specific term (non-common word)
            common_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'is',
                'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
                'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might',
                'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
                'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where',
                'why', 'how', 'tell', 'me', 'explain',
            }
            
            specific_words = [w for w in words if w not in common_words and len(w) > 2]
            if len(specific_words) <= 1:
                return True
        
        return False

    def generate_clarifying_prompt(self, question: str) -> str:
        """
        Generate a clarifying prompt to help disambiguate the query.
        
        Args:
            question: The ambiguous user question
            
        Returns:
            A helpful prompt asking for more details
        """
        return (
            f"Your question '{question}' could refer to several topics. "
            "Could you please provide more details or context? For example:\n"
            "- What specific aspect are you interested in?\n"
            "- Is this related to a particular system, process, or tool?\n"
            "- Are you looking for step-by-step instructions or conceptual information?"
        )

    def has_sufficient_context(self, sections: list[str]) -> bool:
        """Determine if retrieved sections provide enough context."""

        if not sections:
            return False

        total_chars = sum(len(section.strip()) for section in sections if section)
        return total_chars >= self.min_context_chars

    def build_fallback_message(self, question: str) -> str:
        """Generate a user-facing fallback message."""

        return (
            "I'm sorry, I couldn't find enough information in the knowledge base "
            f"to answer '{question}'. Please try rephrasing your question or explore "
            "the related topics below."
        )

    def answer(self, question: str, sections: list[str]) -> AnswerResult:
        """
        Generate an answer from retrieved sections, with ambiguity detection.
        
        Args:
            question: User's question
            sections: Retrieved section contents
            
        Returns:
            Structured answer result including fallback status
        """
        # Check for ambiguity
        if self.is_ambiguous(question):
            # If no good context found, ask for clarification
            if not sections:
                clarifying_prompt = self.generate_clarifying_prompt(question)
                return AnswerResult(
                    response_id=str(uuid.uuid4()),
                    generated_text=clarifying_prompt,
                    clarification_required=True,
                )

        if not self.has_sufficient_context(sections):
            fallback_message = self.build_fallback_message(question)
            return AnswerResult(
                response_id=str(uuid.uuid4()),
                generated_text=fallback_message,
                is_fallback=True,
            )
        
        # Build context and generate answer
        context = "\n".join(sections)
        
        # Enhanced prompt with instructions for handling ambiguity
        prompt = (
            f"CONTEXT:\n{context}\n\n"
            f"QUESTION: {question}\n\n"
            "INSTRUCTIONS: Provide a clear, accurate answer based on the "
            "context above. If the question is ambiguous or could have "
            "multiple interpretations, acknowledge the ambiguity and address "
            "the most likely interpretation based on the context. If the "
            "context doesn't contain enough information to answer confidently, "
            "say so clearly.\n\n"
            "ANSWER:"
        )
        
        generated = self.provider.generate(prompt)
        return AnswerResult(
            response_id=str(uuid.uuid4()),
            generated_text=generated,
        )
