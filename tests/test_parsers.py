"""Tests for document parsers."""

import pytest
from pathlib import Path

from rag_system.parsers import DoclingParser


@pytest.fixture
def parser():
    """Create parser instance."""
    return DoclingParser()


def test_parser_initialization(parser):
    """Test parser initialization."""
    assert parser is not None
    assert parser.converter is not None


def test_parse_nonexistent_file(parser):
    """Test parsing non-existent file."""
    with pytest.raises(FileNotFoundError):
        parser.parse("nonexistent.pdf")


# Note: Add more tests with actual PDF files when available
