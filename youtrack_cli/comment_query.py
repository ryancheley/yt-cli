"""Filtering of issue comments by a small ``--query`` expression.

Supported terms, combined with ``and`` (the only connector):

* ``@name`` – the comment text contains that at-mention.
* ``created OP DATE`` – the comment's ``created`` timestamp (epoch
  milliseconds) compared against an ISO ``YYYY-MM-DD`` date, where ``OP`` is
  one of ``>``, ``<``, ``>=``, ``<=``. The date is interpreted as local
  start-of-day.

Example: ``@ryan and created >= 2026-01-01 and created < 2026-06-01``
"""

from __future__ import annotations

import operator
import re
from collections.abc import Callable
from datetime import datetime
from typing import Any

_CREATED_RE = re.compile(r"^created\s*(>=|<=|>|<)\s*(\d{4}-\d{2}-\d{2})$")
_OPS: dict[str, Callable[[Any, Any], bool]] = {
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
}


class QueryError(ValueError):
    """Raised when a ``--query`` expression cannot be parsed."""


def _date_to_epoch_ms(date_str: str) -> int:
    """Convert an ISO ``YYYY-MM-DD`` date to local start-of-day epoch ms."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return int(dt.timestamp() * 1000)


def _created_predicate(op: str, threshold_ms: int) -> Callable[[dict[str, Any]], bool]:
    compare = _OPS[op]

    def predicate(comment: dict[str, Any]) -> bool:
        created = comment.get("created")
        if created is None:
            return False
        return compare(int(created), threshold_ms)

    return predicate


def _mention_predicate(mention: str) -> Callable[[dict[str, Any]], bool]:
    # Anchor on a trailing non-word boundary so ``@ryan`` does not match
    # ``@ryanc``. ``-`` is treated as part of a name (logins may contain it).
    pattern = re.compile(re.escape(mention) + r"(?![\w-])")

    def predicate(comment: dict[str, Any]) -> bool:
        return bool(pattern.search(comment.get("text") or ""))

    return predicate


def build_predicates(query: str) -> list[Callable[[dict[str, Any]], bool]]:
    """Parse ``query`` into a list of per-comment predicates.

    Raises:
        QueryError: if any term is not a supported ``@mention`` or
            ``created OP DATE`` expression.
    """
    terms = [t.strip() for t in re.split(r"\s+and\s+", query.strip(), flags=re.IGNORECASE) if t.strip()]
    if not terms:
        raise QueryError("Query is empty.")

    predicates: list[Callable[[dict[str, Any]], bool]] = []
    for term in terms:
        created_match = _CREATED_RE.match(term)
        if created_match:
            op, date_str = created_match.group(1), created_match.group(2)
            predicates.append(_created_predicate(op, _date_to_epoch_ms(date_str)))
        elif term.startswith("@") and len(term) > 1:
            predicates.append(_mention_predicate(term))
        else:
            raise QueryError(
                f"Invalid query term: {term!r}. "
                "Expected an @mention or a 'created OP YYYY-MM-DD' expression joined by 'and'."
            )
    return predicates


def filter_comments(comments: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    """Return the comments matching every term in ``query``."""
    predicates = build_predicates(query)
    return [c for c in comments if all(p(c) for p in predicates)]


def _demo() -> None:
    comments = [
        {"text": "hello @ryan", "created": _date_to_epoch_ms("2026-03-01")},
        {"text": "ping @ryanc", "created": _date_to_epoch_ms("2026-03-01")},
        {"text": "hi @ryan again", "created": _date_to_epoch_ms("2025-12-01")},
    ]
    # @mention alone
    assert [c["text"] for c in filter_comments(comments, "@ryan")] == ["hello @ryan", "hi @ryan again"]
    # @mention does not match a longer login
    assert filter_comments(comments, "@ryan and created > 2026-01-01") == [comments[0]]
    # date range
    assert filter_comments(comments, "created >= 2026-01-01 and created < 2026-06-01") == [
        comments[0],
        comments[1],
    ]
    # invalid term
    try:
        filter_comments(comments, "author: bob")
    except QueryError:
        pass
    else:  # pragma: no cover
        raise AssertionError("expected QueryError")
    print("ok")


if __name__ == "__main__":
    _demo()
