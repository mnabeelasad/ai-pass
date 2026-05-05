"""
Tool: AnalysisTool
Uses an LLM to analyze a document given retrieved context.
Returns a structured analysis summary.
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.config import settings
from app.core.logger import get_logger
from typing import List

logger = get_logger(__name__)

ANALYSIS_SYSTEM_PROMPT = """You are an expert document analyst.
Your job is to analyze a given document and summarize its key facts,
claims, risks, and relevant content based on the provided context chunks.
Be factual and concise. Focus on content that relates to policy compliance."""


def analysis_tool(
    document_text: str,
    retrieved_context: List[str],
) -> str:
    """
    Analyzes the input document using retrieved RAG context.

    Args:
        document_text: The original input document
        retrieved_context: Chunks from the vector store

    Returns:
        A structured analysis summary string
    """
    context_block = "\n\n---\n\n".join(retrieved_context) if retrieved_context else "No context retrieved."

    user_prompt = f"""
Document to analyze:
{document_text}

Relevant context retrieved from knowledge base:
{context_block}

Provide:
1. Key facts/claims in the document
2. Potential risks or red flags
3. What is missing or unclear
4. Overall assessment summary
"""

    llm = ChatOpenAI(
        model=settings.openai_model,
        openai_api_key=settings.openai_api_key,
        temperature=0.2,
    )

    logger.info("[AnalysisTool] Sending document to LLM for analysis")
    response = llm.invoke([
        SystemMessage(content=ANALYSIS_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ])

    analysis = response.content
    logger.info(f"[AnalysisTool] Analysis complete ({len(analysis)} chars)")
    return analysis