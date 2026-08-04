"""Tests for the ``yt issues comments list --query`` filter."""

from datetime import datetime

import pytest

from youtrack_cli.comment_query import QueryError, filter_comments


def _ms(date_str: str) -> int:
    return int(datetime.strptime(date_str, "%Y-%m-%d").timestamp() * 1000)


@pytest.fixture
def comments():
    return [
        {"id": "1", "text": "hello @ryan", "created": _ms("2026-03-01")},
        {"id": "2", "text": "ping @ryanc", "created": _ms("2026-03-01")},
        {"id": "3", "text": "hi @ryan again", "created": _ms("2025-12-01")},
        {"id": "4", "text": "no mention here", "created": _ms("2026-05-01")},
    ]


def test_mention_matches_exact_login_only(comments):
    result = filter_comments(comments, "@ryan")
    assert [c["id"] for c in result] == ["1", "3"]


def test_created_greater_than(comments):
    result = filter_comments(comments, "created > 2026-01-01")
    assert [c["id"] for c in result] == ["1", "2", "4"]


def test_created_range_with_bounds(comments):
    result = filter_comments(comments, "created >= 2026-01-01 and created < 2026-04-01")
    assert [c["id"] for c in result] == ["1", "2"]


def test_mention_and_date_combined(comments):
    result = filter_comments(comments, "@ryan and created > 2026-01-01")
    assert [c["id"] for c in result] == ["1"]


def test_and_is_case_insensitive(comments):
    result = filter_comments(comments, "@ryan AND created > 2026-01-01")
    assert [c["id"] for c in result] == ["1"]


def test_comment_missing_created_is_excluded_by_date_term():
    result = filter_comments([{"id": "x", "text": "@ryan"}], "created > 2020-01-01")
    assert result == []


def test_invalid_term_raises():
    with pytest.raises(QueryError):
        filter_comments([], "author: bob")


def test_invalid_date_raises():
    with pytest.raises(ValueError):
        filter_comments([], "created > 2026-13-40")
