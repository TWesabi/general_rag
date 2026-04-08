from unittest.mock import MagicMock, patch

import httpx
import pytest

from src.embeddings.embedding import OllamaEmbedder


@patch("src.embeddings.embedding.httpx.post")
def test_embedding(mock_post):

    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {
            "data": [
                {"embedding": [1.0, 2.0, 3.0]},
                {"embedding": [4.0, 5.0, 6.0]},
            ]
        },
    )

    embedder = OllamaEmbedder()
    result = embedder(["hello", "world"])

    assert len(result) == 2
    assert result[0] == [1.0, 2.0, 3.0]


def test_empty_list():
    embdder = OllamaEmbedder()
    text_lists = []
    with pytest.raises(ValueError):
        embdder(text_list=text_lists)


@patch("src.embeddings.embedding.httpx.post")
def test_url_and_model(mock_post):

    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {
            "data": [
                {"embedding": [1.0, 2.0, 3.0]},
                {"embedding": [4.0, 5.0, 6.0]},
            ]
        },
    )
    embedder = OllamaEmbedder()

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args

    assert "embeddings" in args[0]
    assert kwargs["json"]["input"] == ["hello", "world"]
    assert kwargs["json"]["model"] == embedder.model


@patch("src.embeddings.embedding.httpx.post")
def test_connection(mock_post):
    mock_post.side_effect = httpx.ConnectError("Connection refused")

    embedder = OllamaEmbedder()
    with pytest.raises(httpx.ConnectError):
        embedder(["hello", "world"])
