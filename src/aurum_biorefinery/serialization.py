"""Strict JSON loading and stable result serialization."""

from __future__ import annotations

import json
from dataclasses import fields, is_dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

from .model import CampaignResult, Scenario, ScenarioError


def load_scenario(path: str | Path) -> Scenario:
    source = Path(path)
    try:
        raw = json.loads(source.read_text(encoding="utf-8"), parse_float=Decimal, parse_int=Decimal)
    except OSError as exc:
        raise ScenarioError(f"unable to read scenario {source}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ScenarioError(f"invalid JSON in {source}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ScenarioError("scenario root must be a JSON object")
    return Scenario.from_mapping(raw)


def _plain(value: Any) -> Any:
    if isinstance(value, Decimal):
        return format(value, "f")
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: _plain(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, list):
        return [_plain(item) for item in value]
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    return value


def result_document(result: CampaignResult) -> dict[str, Any]:
    document = _plain(result)
    if not isinstance(document, dict):
        raise TypeError("campaign result did not serialize to an object")
    document["schema_version"] = "aurum.result.v1"
    return document


def dumps_result(result: CampaignResult, *, pretty: bool = False) -> str:
    separators = None if pretty else (",", ":")
    return json.dumps(
        result_document(result),
        indent=2 if pretty else None,
        separators=separators,
        sort_keys=True,
    )

