"""Tests for DataFeed class."""
import pytest
from unittest.mock import Mock, patch
from src.data.data_feed import DataFeed


def test_datafeed_initialization():
    """Test DataFeed initialization."""
    feed = DataFeed(source="tushare", token="fake_token")
    assert feed.source == "tushare"
    assert feed.token == "fake_token"


def test_unsupported_data_source():
    """Test unsupported data source raises error."""
    with pytest.raises(ValueError, match="Unsupported data source"):
        DataFeed(source="unsupported", token="fake_token")