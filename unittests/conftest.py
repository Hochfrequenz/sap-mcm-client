"""Shared fixtures for SAP MCM client unit tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

TESTDATA = Path(__file__).resolve().parent.parent / "testdata"


def _load_json(name: str) -> dict[str, Any]:
    """Load a JSON fixture from the testdata directory."""
    return json.loads((TESTDATA / name).read_text(encoding="utf-8"))


@pytest.fixture()
def instance_get_json() -> dict[str, Any]:
    """Raw JSON for a single instance GET response (with OData envelope)."""
    return _load_json("instance_get.json")


@pytest.fixture()
def instance_list_json() -> dict[str, Any]:
    """Raw JSON for an instance list response."""
    return _load_json("instance_list.json")


@pytest.fixture()
def class_get_json() -> dict[str, Any]:
    """Raw JSON for a single class GET response."""
    return _load_json("class_get.json")


@pytest.fixture()
def class_list_json() -> dict[str, Any]:
    """Raw JSON for a class list response."""
    return _load_json("class_list.json")


@pytest.fixture()
def model_get_json() -> dict[str, Any]:
    """Raw JSON for a single model GET response."""
    return _load_json("model_get.json")


@pytest.fixture()
def model_list_json() -> dict[str, Any]:
    """Raw JSON for a model list response."""
    return _load_json("model_list.json")


@pytest.fixture()
def error_401_json() -> dict[str, Any]:
    """Raw JSON for a 401 error response."""
    return _load_json("error_401.json")


@pytest.fixture()
def error_403_json() -> dict[str, Any]:
    """Raw JSON for a 403 error response."""
    return _load_json("error_403.json")


@pytest.fixture()
def error_404_json() -> dict[str, Any]:
    """Raw JSON for a 404 error response."""
    return _load_json("error_404.json")
