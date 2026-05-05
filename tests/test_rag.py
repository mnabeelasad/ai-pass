"""
Unit tests for RAG pipeline components.
"""
import pytest
from app.rag.embedder import chunk_text


def test_chunk_text_basic():
    text = " ".join([f"word{i}" for i in range(1000)])
    chunks = chunk_text(text, chunk_size=100, overlap=10)
    assert len(chunks) > 1
    for chunk in chunks:
        assert isinstance(chunk, str)
        assert len(chunk) > 0


def test_chunk_text_short_input():
    text = "This is a short document."
    chunks = chunk_text(text, chunk_size=100, overlap=10)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunk_overlap():
    words = [f"w{i}" for i in range(20)]
    text = " ".join(words)
    chunks = chunk_text(text, chunk_size=10, overlap=2)
    # Ensure we have more than one chunk due to sliding window
    assert len(chunks) >= 2